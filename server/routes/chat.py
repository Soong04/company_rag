# ============================================================================
# 对话/问答路由
# ============================================================================
from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from flask_login import login_required, current_user
from models import db, Conversation, Message, SysLog, Feedback
from datetime import datetime
import time

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# ---------- 流式问答常量 ----------
_STREAM_TIMEOUT = 300          # 单次问答最长 300 秒（CPU推理较慢）
_TOKEN_IDLE_TIMEOUT = 120      # 两次 token 之间最多等待 120 秒


@chat_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    """
    发起问答（调用 RAG 流程）
    POST /api/chat/ask
    Body: {"question": "xxx", "conversation_id": 1 (可选)}
    """
    data = request.get_json()
    if not data or not data.get('question', '').strip():
        return jsonify({'code': 400, 'message': '请输入问题'}), 400

    question = data['question'].strip()
    conversation_id = data.get('conversation_id')

    # 如果没有对话ID，创建新对话
    if not conversation_id:
        # 自动生成对话标题（取问题前20字）
        title = question[:20] + '...' if len(question) > 20 else question
        conversation = Conversation(
            user_id=current_user.id,
            title=title,
            model_name='qwen2.5:7b'
        )
        db.session.add(conversation)
        db.session.commit()
        conversation_id = conversation.id
    else:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'code': 404, 'message': '对话不存在'}), 404
        if conversation.user_id != current_user.id and not current_user.is_admin():
            return jsonify({'code': 403, 'message': '无权访问该对话'}), 403

    # 保存用户问题
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=question
    )
    db.session.add(user_message)
    db.session.commit()

    # 调用 RAG 服务（使用全局单例）
    answer_data = {'answer': '', 'sources': []}
    try:
        from app import get_rag_service
        rag_service = get_rag_service()
        if rag_service is None:
            raise RuntimeError('RAG 服务未初始化')

        answer_data = rag_service.ask(
            question=question,
            top_k=current_app.config.get('RETRIEVAL_TOP_K', 5)
        )
    except Exception as e:
        # 如果 RAG 服务不可用，返回提示
        answer_data = {
            'answer': f'抱歉，问答服务暂时不可用：{str(e)}。请确保 Ollama 服务已启动且模型已加载。',
            'sources': []
        }

    # 保存 AI 回答
    assistant_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=answer_data.get('answer', ''),
        source_docs=answer_data.get('sources', []),
        tokens_used=answer_data.get('tokens_used', 0)
    )
    db.session.add(assistant_message)
    db.session.flush()
    assistant_message_id = assistant_message.id

    # 更新对话信息
    conversation.message_count = Message.query.filter_by(conversation_id=conversation_id).count()
    db.session.commit()

    # 记录操作日志
    log = SysLog(
        user_id=current_user.id,
        action='query',
        detail=f'问答查询：{question[:50]}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'code': 200,
        'data': {
            'conversation_id': conversation_id,
            'question': question,
            'answer': answer_data.get('answer', ''),
            'sources': answer_data.get('sources', []),
            'model': answer_data.get('model', 'qwen2.5:7b'),
            'message_id': assistant_message_id,
        }
    })


@chat_bp.route('/stream', methods=['POST'])
@login_required
def ask_stream():
    """
    流式问答接口（SSE）
    POST /api/chat/stream
    Body: {"question": "xxx", "conversation_id": 1 (可选)}
    """
    data = request.get_json()
    if not data or not data.get('question', '').strip():
        return jsonify({'code': 400, 'message': '请输入问题'}), 400

    question = data['question'].strip()
    conversation_id = data.get('conversation_id')
    current_user_id = current_user.id

    # 创建或获取对话
    if not conversation_id:
        title = question[:20] + '...' if len(question) > 20 else question
        conversation = Conversation(user_id=current_user_id, title=title, model_name='qwen2.5:7b')
        db.session.add(conversation)
        db.session.commit()
        conversation_id = conversation.id
    else:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'code': 404, 'message': '对话不存在'}), 404
        if conversation.user_id != current_user_id and not current_user.is_admin():
            return jsonify({'code': 403, 'message': '无权访问该对话'}), 403

    # 保存用户消息
    user_message = Message(conversation_id=conversation_id, role='user', content=question)
    db.session.add(user_message)
    db.session.commit()

    def generate():
        full_answer = ''
        sources_data = []
        saved = False  # 标记是否已保存到数据库
        client_connected = True  # 客户端是否还在连接
        remote_ip = request.remote_addr  # 提前捕获，避免 finally 中 request 不可用
        start_time = time.time()
        last_token_time = time.time()

        try:
            from app import get_rag_service
            rag_service = get_rag_service()
            if rag_service is None:
                raise RuntimeError('RAG 服务未初始化')

            for event in rag_service.ask_stream(question, current_app.config.get('RETRIEVAL_TOP_K', 5)):
                import json

                # ---- 超时检查 ----
                now = time.time()
                if now - start_time > 180:
                    timeout_msg = '\n\n[回答超时，请简化问题或重试]'
                    full_answer += timeout_msg
                    try:
                        yield f"data: {json.dumps({'type': 'token', 'data': timeout_msg}, ensure_ascii=False)}\n\n"
                    except GeneratorExit:
                        client_connected = False
                    break

                if now - last_token_time > 45:
                    idle_msg = '\n\n[回答断开，模型响应中断，请重试]'
                    full_answer += idle_msg
                    try:
                        yield f"data: {json.dumps({'type': 'token', 'data': idle_msg}, ensure_ascii=False)}\n\n"
                    except GeneratorExit:
                        client_connected = False
                    break

                if event['type'] == 'sources':
                    sources_data = event['data']
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                elif event['type'] == 'token':
                    full_answer += event['data']
                    last_token_time = time.time()
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                elif event['type'] == 'done':
                    full_answer = event['data'].get('answer', full_answer)

        except GeneratorExit:
            # 客户端断开连接——标记退出，不再 yield
            client_connected = False
        except Exception as e:
            import json
            error_msg = f'抱歉，问答服务暂时不可用：{str(e)}'
            full_answer = error_msg
            try:
                yield f"data: {json.dumps({'type': 'token', 'data': error_msg}, ensure_ascii=False)}\n\n"
            except GeneratorExit:
                client_connected = False

        finally:
            # 确保无论如何都将（部分）回答保存到数据库
            if not saved and full_answer.strip():
                _save_stream_result(
                    conversation_id, current_user_id,
                    question, full_answer, sources_data,
                    remote_ip
                )
                saved = True

        # 客户端还在连接时才发送完成事件
        if client_connected:
            import json
            yield f"data: {json.dumps({'type': 'done', 'data': {'conversation_id': conversation_id}}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@chat_bp.route('/history', methods=['GET'])
@login_required
def get_conversations():
    """
    获取历史对话列表
    GET /api/chat/history?page=1&size=20&keyword=xxx
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    keyword = request.args.get('keyword', '').strip()

    query = Conversation.query.filter_by(user_id=current_user.id)
    if keyword:
        query = query.filter(Conversation.title.like(f'%{keyword}%'))
    pagination = query.order_by(Conversation.update_time.desc()).paginate(
        page=page, per_page=size, error_out=False
    )

    conversations = [conv.to_dict() for conv in pagination.items]

    return jsonify({
        'code': 200,
        'data': {
            'list': conversations,
            'total': pagination.total,
            'page': page,
            'size': size
        }
    })


@chat_bp.route('/history/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation_detail(conversation_id):
    """
    获取单条对话详情（包含所有消息）
    GET /api/chat/history/<id>
    """
    conversation = Conversation.query.get_or_404(conversation_id)

    # 权限检查
    if conversation.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'code': 403, 'message': '无权访问该对话'}), 403

    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.create_time).all()

    message_list = []
    for msg in messages:
        msg_dict = {
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'source_docs': msg.source_docs if msg.source_docs else None,
            'tokens_used': msg.tokens_used,
            'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        message_list.append(msg_dict)

    return jsonify({
        'code': 200,
        'data': {
            'conversation': conversation.to_dict(),
            'messages': message_list
        }
    })


@chat_bp.route('/history/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """
    删除对话
    DELETE /api/chat/history/<id>
    """
    conversation = Conversation.query.get_or_404(conversation_id)

    if conversation.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'code': 403, 'message': '无权删除该对话'}), 403

    # 级联删除消息
    Message.query.filter_by(conversation_id=conversation_id).delete()
    db.session.delete(conversation)
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


@chat_bp.route('/feedback', methods=['POST'])
@login_required
def add_feedback():
    """
    提交问答反馈（赞/踩）
    POST /api/chat/feedback
    Body: {"message_id": 1, "rating": 1, "comment": ""}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据为空'}), 400

    message_id = data.get('message_id')
    rating = data.get('rating')

    if not message_id:
        return jsonify({'code': 400, 'message': '缺少 message_id'}), 400
    if rating not in (1, -1):
        return jsonify({'code': 400, 'message': '评分只能为 1（赞）或 -1（踩）'}), 400

    # 检查消息是否存在且属于当前用户
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'code': 404, 'message': '消息不存在'}), 404

    # 更新已有反馈或创建新反馈
    existing = Feedback.query.filter_by(
        message_id=message_id, user_id=current_user.id
    ).first()

    if existing:
        existing.rating = rating
        existing.comment = data.get('comment', '')
        db.session.commit()
        return jsonify({'code': 200, 'message': '反馈已更新', 'data': {'feedback': existing.to_dict()}})

    feedback = Feedback(
        message_id=message_id,
        user_id=current_user.id,
        rating=rating,
        comment=data.get('comment', ''),
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'code': 200, 'message': '反馈提交成功', 'data': {'feedback': feedback.to_dict()}})


def _save_stream_result(conversation_id, user_id, question, answer, sources, ip):
    """
    保存流式问答结果到数据库（供 generate() 在 finally 中调用）
    客户端断开连接时也能保存部分回答，避免出现已保存问题但无回答的情况
    """
    try:
        with current_app.app_context():
            assistant_msg = Message(
                conversation_id=conversation_id, role='assistant',
                content=answer or '(回答被中断)',
                source_docs=sources
            )
            db.session.add(assistant_msg)
            db.session.flush()

            conv = Conversation.query.get(conversation_id)
            if conv:
                conv.message_count = Message.query.filter_by(conversation_id=conversation_id).count()
            db.session.commit()

            log = SysLog(
                user_id=user_id, action='query',
                detail=f'问答查询：{question[:50]}',
                ip_address=ip
            )
            db.session.add(log)
            db.session.commit()
    except Exception:
        db.session.rollback()
