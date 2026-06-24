<template>
    <canvas ref="canvasRef" class="particle-bg"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animId = null
let resizeHandler = null

onMounted(() => {
    const canvas = canvasRef.value
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let w = window.innerWidth
    let h = window.innerHeight
    canvas.width = w
    canvas.height = h

    const COUNT = 60
    const particles = Array.from({ length: COUNT }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        r: Math.random() * 2 + 1.2,
    }))

    const R = 99, G = 102, B = 241

    function draw() {
        ctx.clearRect(0, 0, w, h)
        for (const p of particles) {
            p.x += p.vx
            p.y += p.vy
            if (p.x < 0 || p.x > w) p.vx *= -1
            if (p.y < 0 || p.y > h) p.vy *= -1
            ctx.beginPath()
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
            ctx.fillStyle = `rgba(${R}, ${G}, ${B}, 0.5)`
            ctx.fill()
        }
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x
                const dy = particles[i].y - particles[j].y
                const dist = Math.sqrt(dx * dx + dy * dy)
                if (dist < 150) {
                    ctx.beginPath()
                    ctx.moveTo(particles[i].x, particles[i].y)
                    ctx.lineTo(particles[j].x, particles[j].y)
                    ctx.strokeStyle = `rgba(${R}, ${G}, ${B}, ${(1 - dist / 150) * 0.2})`
                    ctx.lineWidth = 0.6
                    ctx.stroke()
                }
            }
        }
        animId = requestAnimationFrame(draw)
    }

    draw()

    resizeHandler = function () {
        w = window.innerWidth
        h = window.innerHeight
        canvas.width = w
        canvas.height = h
    }
    window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
    if (animId) cancelAnimationFrame(animId)
    if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})
</script>

<style scoped>
.particle-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
}
</style>
