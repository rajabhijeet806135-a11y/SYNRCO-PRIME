import React, { useEffect, useRef } from 'react';

interface Star {
  x: number;
  y: number;
  size: number;
  opacity: number;
  twinkleSpeed: number;
  color: string;
}

interface ShootingStar {
  x: number;
  y: number;
  length: number;
  speed: number;
  angle: number;
  opacity: number;
}

export const CosmicStarfield: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Generate Stars
    const starColors = ['#ffffff', '#00f0ff', '#c77dff', '#ffd166', '#a0c4ff'];
    const stars: Star[] = Array.from({ length: 180 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 1.8 + 0.3,
      opacity: Math.random() * 0.7 + 0.2,
      twinkleSpeed: Math.random() * 0.02 + 0.005,
      color: starColors[Math.floor(Math.random() * starColors.length)]
    }));

    const shootingStars: ShootingStar[] = [];

    const maybeAddShootingStar = () => {
      if (Math.random() < 0.015 && shootingStars.length < 3) {
        shootingStars.push({
          x: Math.random() * width * 0.8,
          y: Math.random() * height * 0.4,
          length: Math.random() * 80 + 50,
          speed: Math.random() * 10 + 12,
          angle: Math.PI / 4 + (Math.random() * 0.2 - 0.1),
          opacity: 1
        });
      }
    };

    let tick = 0;
    const render = () => {
      tick++;
      ctx.clearRect(0, 0, width, height);

      // Deep Space Nebulae Glow
      const grad1 = ctx.createRadialGradient(width * 0.2, height * 0.2, 50, width * 0.2, height * 0.2, 450);
      grad1.addColorStop(0, 'rgba(157, 78, 221, 0.09)');
      grad1.addColorStop(1, 'transparent');
      ctx.fillStyle = grad1;
      ctx.fillRect(0, 0, width, height);

      const grad2 = ctx.createRadialGradient(width * 0.85, height * 0.75, 40, width * 0.85, height * 0.75, 550);
      grad2.addColorStop(0, 'rgba(0, 240, 255, 0.08)');
      grad2.addColorStop(1, 'transparent');
      ctx.fillStyle = grad2;
      ctx.fillRect(0, 0, width, height);

      const grad3 = ctx.createRadialGradient(width * 0.5, height * 0.9, 20, width * 0.5, height * 0.9, 400);
      grad3.addColorStop(0, 'rgba(255, 0, 85, 0.05)');
      grad3.addColorStop(1, 'transparent');
      ctx.fillStyle = grad3;
      ctx.fillRect(0, 0, width, height);

      // Render Stars
      stars.forEach(star => {
        const currentOpacity = star.opacity + Math.sin(tick * star.twinkleSpeed) * 0.25;
        ctx.fillStyle = star.color;
        ctx.globalAlpha = Math.max(0.1, Math.min(1, currentOpacity));
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();
      });

      // Render & Update Shooting Stars
      maybeAddShootingStar();
      for (let i = shootingStars.length - 1; i >= 0; i--) {
        const ss = shootingStars[i];
        const endX = ss.x + Math.cos(ss.angle) * ss.length;
        const endY = ss.y + Math.sin(ss.angle) * ss.length;

        const ssGrad = ctx.createLinearGradient(ss.x, ss.y, endX, endY);
        ssGrad.addColorStop(0, `rgba(0, 240, 255, ${ss.opacity})`);
        ssGrad.addColorStop(1, 'transparent');

        ctx.strokeStyle = ssGrad;
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = ss.opacity;
        ctx.beginPath();
        ctx.moveTo(ss.x, ss.y);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        ss.x += Math.cos(ss.angle) * ss.speed;
        ss.y += Math.sin(ss.angle) * ss.speed;
        ss.opacity -= 0.02;

        if (ss.opacity <= 0 || ss.x > width || ss.y > height) {
          shootingStars.splice(i, 1);
        }
      }

      ctx.globalAlpha = 1.0;
      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0 opacity-80"
      style={{ background: 'transparent' }}
    />
  );
};
