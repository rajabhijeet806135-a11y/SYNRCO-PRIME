import React, { useEffect, useRef } from 'react';
import { Activity, Cpu, Database, Compass } from 'lucide-react';
import { MatchInfo, MatchTelemetry } from '../../types';

interface HardcoreAnalyticsHubProps {
  match: MatchInfo;
  telemetry: MatchTelemetry | null;
  onOpenHistorical: () => void;
}

export const HardcoreAnalyticsHub: React.FC<HardcoreAnalyticsHubProps> = ({
  match,
  telemetry,
  onOpenHistorical
}) => {
  const radarCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const isCricket = match.sport === 'CRICKET';

  // 2D Tactical Field Radar Loop
  useEffect(() => {
    const canvas = radarCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let tick = 0;

    const render = () => {
      tick++;
      const w = (canvas.width = canvas.parentElement?.clientWidth || 280);
      const h = (canvas.height = 160);

      ctx.clearRect(0, 0, w, h);

      // Radar Screen Background
      ctx.fillStyle = '#060a16';
      ctx.fillRect(0, 0, w, h);

      // Grid lines
      ctx.strokeStyle = 'rgba(157, 78, 221, 0.12)';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 25) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += 25) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Radar Concentric Circles
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.25)';
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, 35, 0, Math.PI * 2);
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(w / 2, h / 2, 65, 0, Math.PI * 2);
      ctx.stroke();

      // Sweeper Scanner Beam
      const angle = (tick * 0.035) % (Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(w / 2, h / 2);
      ctx.lineTo(w / 2 + Math.cos(angle) * 65, h / 2 + Math.sin(angle) * 65);
      ctx.stroke();

      // Players Blips
      if (telemetry?.players) {
        telemetry.players.forEach((p) => {
          const px = (p.x / 100) * w;
          const py = (p.y / 100) * h;
          ctx.fillStyle = p.team === 'home' ? '#00f0ff' : '#ff0055';
          ctx.beginPath();
          ctx.arc(px, py, 3.5, 0, Math.PI * 2);
          ctx.fill();

          ctx.fillStyle = '#ffffff';
          ctx.font = '9px SF Mono, monospace';
          ctx.fillText(p.name.split(' ')[1] || p.name, px + 5, py + 3);
        });
      }

      // Ball Blip
      if (telemetry?.ball) {
        const bx = (telemetry.ball.x / 100) * w;
        const by = (telemetry.ball.y / 100) * h;
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        ctx.arc(bx, by, 4.5, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [telemetry]);

  const ballSpeed = telemetry?.ball?.speedKmh || (telemetry?.ball as any)?.speed_kmh || 144.2;

  return (
    <div className="space-y-3 animate-fade-in">
      
      {/* Telemetry Matrix Card */}
      <div className="glass-panel p-4 border border-purple-500/40 shadow-[0_0_25px_rgba(157,78,221,0.12)]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/30">
              <Activity className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h4 className="text-xs font-display font-bold text-white">
                TACTICAL TELEMETRY & EXPECTED METRICS
              </h4>
              <p className="text-[10px] text-purple-300/80 font-mono">
                25Hz Optical Tracking • High Frequency CQRS
              </p>
            </div>
          </div>

          <button
            onClick={onOpenHistorical}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-200 border border-purple-500/40 text-[11px] font-mono transition-all cursor-pointer"
          >
            <Database className="w-3.5 h-3.5" />
            <span>H2H Dataset 4</span>
          </button>
        </div>

        {/* 2D Canvas Radar + Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 mb-2.5">
          
          <div className="rounded-xl overflow-hidden border border-white/10 relative">
            <canvas ref={radarCanvasRef} className="w-full h-40 block" />
            <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 text-[9px] font-mono text-cyan-300 border border-white/10">
              TACTICAL RADAR 25Hz
            </div>
            <div className="absolute bottom-2 right-2 text-[10px] font-mono text-amber-300">
              BALL: {ballSpeed} km/h
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-black/40 border border-white/10">
              <div className="text-[10px] text-slate-400">EXPECTED METRIC</div>
              <div className="text-sm font-black font-display text-cyan-300 mt-0.5">
                {telemetry?.tacticalAnalysis?.expectedMetricLabel || (isCricket ? 'xWicket' : 'xG')}
              </div>
              <div className="text-xs font-bold text-white">
                {telemetry?.tacticalAnalysis?.expectedMetricValue || (isCricket ? '0.72' : '2.14')}
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-black/40 border border-white/10">
              <div className="text-[10px] text-slate-400">WIN PROB ADDED (WPA)</div>
              <div className="text-sm font-black font-display text-emerald-400 mt-0.5">
                +14.8%
              </div>
              <div className="text-[10px] text-slate-400">High leverage</div>
            </div>

            <div className="p-2.5 rounded-xl bg-black/40 border border-white/10">
              <div className="text-[10px] text-slate-400">BALL SPIN / TRAJECTORY</div>
              <div className="text-xs font-bold text-amber-300 mt-0.5">
                {telemetry?.ball?.spinRpm || (telemetry?.ball as any)?.spin_rpm || 2480} RPM
              </div>
              <div className="text-[10px] text-slate-400">Angle: {telemetry?.ball?.trajectoryAngle || (telemetry?.ball as any)?.trajectory_angle || 31}°</div>
            </div>

            <div className="p-2.5 rounded-xl bg-black/40 border border-white/10">
              <div className="text-[10px] text-slate-400">DEFENSIVE LINE</div>
              <div className="text-xs font-bold text-purple-300 mt-0.5">
                {telemetry?.tacticalAnalysis?.defensiveLineHeightMeters || 46.2}m
              </div>
              <div className="text-[10px] text-slate-400">Pressing Block</div>
            </div>
          </div>

        </div>

        {/* AI Tactical Narrative */}
        <div className="p-2.5 rounded-xl bg-purple-950/20 border border-purple-500/25 text-xs font-mono text-slate-300 flex items-start gap-2">
          <Cpu className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
          <div>
            <span className="font-bold text-purple-300">[AI ANALYST]:</span>{' '}
            {telemetry?.tacticalAnalysis?.aiNarrative || 'High boundary leverage zone detected. Shift to yorker cluster recommended.'}
          </div>
        </div>

      </div>

    </div>
  );
};
