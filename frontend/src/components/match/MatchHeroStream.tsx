import React, { useState, useEffect, useRef } from 'react';
import { 
  Maximize2, 
  Gauge, 
  ShieldAlert, 
  Activity,
  Compass,
  Radio,
  Flame,
  Volume2
} from 'lucide-react';
import { MatchInfo, MatchTelemetry, CameraAngle, PersonaType } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface MatchHeroStreamProps {
  match: MatchInfo;
  telemetry: MatchTelemetry | null;
  currentPersona: PersonaType;
  activeStoppage: string | null;
  onSelectCamera: (cam: CameraAngle) => void;
  activeCamera: CameraAngle;
}

export const MatchHeroStream: React.FC<MatchHeroStreamProps> = ({
  match,
  telemetry,
  currentPersona,
  activeStoppage,
  onSelectCamera,
  activeCamera
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const cameras: { id: CameraAngle; label: string; icon: string }[] = [
    { id: 'MAIN_BROADCAST', label: '4K Broadcast', icon: '🎥' },
    { id: 'SKY_TACTICAL', label: 'Sky Tactical 2D', icon: '🛸' },
    { id: 'PLAYER_POV', label: 'Player Head-Cam', icon: '👤' },
    { id: 'FAN_ENDZONE', label: '360° Fan Endzone', icon: '🏟️' }
  ];

  // High-Fidelity Canvas Broadcast Stream Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let frame = 0;

    const render = () => {
      frame++;
      const w = (canvas.width = canvas.parentElement?.clientWidth || 900);
      const h = (canvas.height = canvas.parentElement?.clientHeight || 500);

      ctx.clearRect(0, 0, w, h);

      if (activeCamera === 'MAIN_BROADCAST') {
        // 1. Stadium Night Arena Background
        const nightGrad = ctx.createLinearGradient(0, 0, 0, h);
        nightGrad.addColorStop(0, '#060a17');
        nightGrad.addColorStop(0.35, '#0a1628');
        nightGrad.addColorStop(0.7, '#071f1b');
        nightGrad.addColorStop(1, '#031410');
        ctx.fillStyle = nightGrad;
        ctx.fillRect(0, 0, w, h);

        // Stadium Floodlights Cones
        ctx.save();
        const lightGrad1 = ctx.createRadialGradient(w * 0.15, 0, 10, w * 0.25, h * 0.5, h * 0.8);
        lightGrad1.addColorStop(0, 'rgba(160, 220, 255, 0.25)');
        lightGrad1.addColorStop(1, 'transparent');
        ctx.fillStyle = lightGrad1;
        ctx.fillRect(0, 0, w, h);

        const lightGrad2 = ctx.createRadialGradient(w * 0.85, 0, 10, w * 0.75, h * 0.5, h * 0.8);
        lightGrad2.addColorStop(0, 'rgba(160, 220, 255, 0.25)');
        lightGrad2.addColorStop(1, 'transparent');
        ctx.fillStyle = lightGrad2;
        ctx.fillRect(0, 0, w, h);
        ctx.restore();

        // Stadium Crowd Silhouette at Top Horizon
        ctx.fillStyle = '#050a14';
        ctx.beginPath();
        ctx.ellipse(w / 2, h * 0.35, w * 0.55, h * 0.12, 0, 0, Math.PI * 2);
        ctx.fill();

        // 2. High-Definition Turf Field Lines
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.ellipse(w / 2, h * 0.65, w * 0.44, h * 0.3, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(w / 2, h * 0.65, w * 0.26, h * 0.18, 0, 0, Math.PI * 2);
        ctx.stroke();

        // 22-Yard Pitch / Central Area
        const pitchGrad = ctx.createLinearGradient(w / 2 - 28, h * 0.52, w / 2 + 28, h * 0.78);
        pitchGrad.addColorStop(0, '#7c5e32');
        pitchGrad.addColorStop(0.5, '#a47e43');
        pitchGrad.addColorStop(1, '#664c26');
        ctx.fillStyle = pitchGrad;
        ctx.fillRect(w / 2 - 24, h * 0.52, 48, 80);
        ctx.strokeStyle = 'rgba(255, 215, 0, 0.6)';
        ctx.strokeRect(w / 2 - 24, h * 0.52, 48, 80);

        // Stumps / Goal lines
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(w / 2 - 8, h * 0.53, 16, 2);
        ctx.fillRect(w / 2 - 8, h * 0.69, 16, 2);

        // 3. Dynamic Player Blips
        const p1x = w / 2 + Math.sin(frame * 0.03) * (w * 0.22);
        const p1y = h * 0.65 + Math.cos(frame * 0.03) * (h * 0.15);
        ctx.fillStyle = '#00f0ff';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 14;
        ctx.beginPath();
        ctx.arc(p1x, p1y, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Player Tag
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText('V. Kohli (78*)', p1x - 28, p1y - 12);

        const p2x = w / 2 - Math.cos(frame * 0.025) * (w * 0.24);
        const p2y = h * 0.65 + Math.sin(frame * 0.025) * (h * 0.16);
        ctx.fillStyle = '#ff0055';
        ctx.shadowColor = '#ff0055';
        ctx.shadowBlur = 14;
        ctx.beginPath();
        ctx.arc(p2x, p2y, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ffffff';
        ctx.fillText('M. Starc (144k)', p2x - 28, p2y - 12);

        // 4. Glowing Ball Trajectory Arc
        const ballSpeed = telemetry?.ball?.speedKmh || (telemetry?.ball as any)?.speed_kmh || 144;
        const progress = (frame % 90) / 90;
        const startX = w / 2;
        const startY = h * 0.53;
        const endX = w / 2 + (w * 0.28);
        const endY = h * 0.72;
        
        // Control point for parabolic flight
        const curX = (1 - progress) * startX + progress * endX;
        const curY = (1 - progress) * startY + progress * endY - Math.sin(progress * Math.PI) * 55;

        // Ball Trail
        ctx.strokeStyle = 'rgba(255, 215, 0, 0.7)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.quadraticCurveTo((startX + endX) / 2, Math.min(startY, endY) - 55, curX, curY);
        ctx.stroke();

        // Glowing Ball
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = '#ffd700';
        ctx.shadowBlur = 22;
        ctx.beginPath();
        ctx.arc(curX, curY, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

      } else if (activeCamera === 'SKY_TACTICAL') {
        // High-Density Tactical Grid
        ctx.fillStyle = '#070b18';
        ctx.fillRect(0, 0, w, h);

        ctx.strokeStyle = 'rgba(157, 78, 221, 0.2)';
        ctx.lineWidth = 1;
        for (let x = 0; x < w; x += 35) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, h);
          ctx.stroke();
        }
        for (let y = 0; y < h; y += 35) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(w, y);
          ctx.stroke();
        }

        // Tactical Heatmap Circle
        const hGrad = ctx.createRadialGradient(w * 0.56, h * 0.52, 10, w * 0.56, h * 0.52, 140);
        hGrad.addColorStop(0, 'rgba(255, 0, 85, 0.45)');
        hGrad.addColorStop(0.5, 'rgba(255, 183, 3, 0.25)');
        hGrad.addColorStop(1, 'transparent');
        ctx.fillStyle = hGrad;
        ctx.fillRect(0, 0, w, h);

        // Radar Scan Arc
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.5)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(w / 2, h / 2, Math.min(w, h) * 0.38, 0, Math.PI * 2);
        ctx.stroke();

      } else if (activeCamera === 'PLAYER_POV') {
        // First Person Helmet POV
        const povGrad = ctx.createRadialGradient(w / 2, h / 2, 60, w / 2, h / 2, w * 0.6);
        povGrad.addColorStop(0, '#0c152a');
        povGrad.addColorStop(1, '#03050a');
        ctx.fillStyle = povGrad;
        ctx.fillRect(0, 0, w, h);

        // Crosshair Targeting
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(w / 2 - 40, h / 2 - 40, 80, 80);
        ctx.beginPath();
        ctx.arc(w / 2, h / 2, 6, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = '#00f0ff';
        ctx.font = 'bold 12px Inter, sans-serif';
        ctx.fillText('TARGET LOCK: OFF-STUMP CORRIDOR', w / 2 - 110, h / 2 + 65);
        ctx.fillStyle = '#ffffff';
        ctx.font = '11px SF Mono, monospace';
        ctx.fillText('SPRINT: 31.8 KM/H  |  HR: 168 BPM', w / 2 - 95, h / 2 + 85);

      } else if (activeCamera === 'FAN_ENDZONE') {
        // 360° Fan Endzone
        const fanGrad = ctx.createLinearGradient(0, 0, 0, h);
        fanGrad.addColorStop(0, '#100824');
        fanGrad.addColorStop(1, '#050308');
        ctx.fillStyle = fanGrad;
        ctx.fillRect(0, 0, w, h);

        for (let i = 0; i < 5; i++) {
          ctx.strokeStyle = `rgba(255, 183, 3, ${0.15 + (i % 3) * 0.12})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          const waveY = h * 0.75 + Math.sin(frame * 0.05 + i) * 15;
          ctx.arc(w / 2, waveY, 70 + i * 45, Math.PI, Math.PI * 2);
          ctx.stroke();
        }
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [activeCamera, telemetry]);

  const ballSpeed = telemetry?.ball?.speedKmh || (telemetry?.ball as any)?.speed_kmh || 144.2;

  return (
    <div className="relative w-full aspect-video rounded-2xl overflow-hidden bg-black border border-white/15 shadow-2xl">
      
      {/* Simulation Render Canvas */}
      <canvas ref={canvasRef} className="w-full h-full block" />

      {/* Top Left: Broadcast Scorebug */}
      <div className="absolute top-2.5 left-2.5 z-20 flex items-center gap-2">
        <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-xl bg-[#080d1e]/90 backdrop-blur-md border border-white/20 shadow-lg text-xs font-mono">
          <span className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-rose-600 text-white text-[9px] font-black tracking-wider shadow-[0_0_10px_rgba(255,0,85,0.6)]">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
            4K
          </span>
          <span className="font-display font-black text-white">
            {match.homeTeam.slice(0, 3).toUpperCase()} <span className="text-cyan-400 font-mono">{match.homeScore.split(' ')[0]}</span>
          </span>
          <span className="text-slate-500 font-bold">·</span>
          <span className="font-display font-black text-white">
            {match.awayTeam.slice(0, 3).toUpperCase()} <span className="text-purple-400 font-mono">{match.awayScore.split(' ')[0]}</span>
          </span>
          <span className="text-[10px] font-mono text-amber-300 bg-amber-500/15 px-1.5 py-0.5 rounded border border-amber-500/30 font-bold">
            {match.gameClock}
          </span>
        </div>
      </div>

      {/* Top Right: Ball Telemetry Readout */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#080d1e]/90 backdrop-blur-md border border-cyan-500/40 text-cyan-300 text-xs font-mono shadow-[0_0_15px_rgba(0,240,255,0.2)]">
          <Gauge className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
          <span>VELOCITY:</span>
          <span className="font-bold text-white font-mono text-sm">
            {ballSpeed} <span className="text-[10px] text-cyan-400 font-normal">km/h</span>
          </span>
        </div>

        <button
          onClick={() => soundSynth.playAlertSound()}
          className="w-8 h-8 rounded-xl bg-black/60 hover:bg-black/90 border border-white/20 hover:border-cyan-400 text-slate-300 hover:text-white flex items-center justify-center transition-all"
          title="Fullscreen"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Center TV Broadcast Stoppage Ticker */}
      {activeStoppage && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#160610]/90 backdrop-blur-md border border-rose-500 text-rose-300 text-xs font-display font-bold shadow-[0_0_30px_rgba(255,0,85,0.7)] animate-pulse">
          <ShieldAlert className="w-4 h-4 text-rose-400" />
          <span>DECISION REVIEW: {activeStoppage.replace(/_/g, ' ')}</span>
          <span className="text-[9px] bg-rose-600 text-white px-2 py-0.5 rounded-full font-mono font-black">
            30s WINDOW
          </span>
        </div>
      )}

      {/* Bottom Center: Camera Perspective Switcher HUD */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1.5 p-1 rounded-xl bg-[#080c18]/90 backdrop-blur-xl border border-white/20 shadow-2xl max-w-[95%] overflow-x-auto">
        {cameras.map((cam) => {
          const isSelected = activeCamera === cam.id;
          return (
            <button
              key={cam.id}
              onClick={() => {
                soundSynth.playAlertSound();
                onSelectCamera(cam.id);
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-display font-bold whitespace-nowrap transition-all ${
                isSelected
                  ? 'bg-cyan-500 text-black shadow-[0_0_15px_rgba(0,240,255,0.6)] font-black scale-105'
                  : 'text-slate-400 hover:text-white hover:bg-white/10'
              }`}
            >
              <span>{cam.icon}</span>
              <span>{cam.label}</span>
            </button>
          );
        })}
      </div>

      {/* Bottom Right: Win Prob Indicator */}
      <div className="absolute bottom-3 right-3 hidden md:flex items-center gap-2 px-3 py-1 rounded-xl bg-black/70 backdrop-blur-md border border-white/15 text-[11px] font-mono text-slate-300 z-20">
        <Activity className="w-3.5 h-3.5 text-emerald-400" />
        <span>WIN PROB:</span>
        <span className="font-bold text-cyan-300 font-mono">
          {match.homeTeam} {match.winProbabilityHome}%
        </span>
      </div>

    </div>
  );
};
