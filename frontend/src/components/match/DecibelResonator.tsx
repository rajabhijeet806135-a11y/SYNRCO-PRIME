import React, { useState, useEffect, useRef } from 'react';
import { Volume2, Flame } from 'lucide-react';
import { CrowdDecibelSnapshot } from '../../types';
import { soundSynth } from '../../services/audioSynth';
import { wsClient } from '../../services/websocket';

interface DecibelResonatorProps {
  matchId: string;
  crowdSnapshot: CrowdDecibelSnapshot | null;
}

export const DecibelResonator: React.FC<DecibelResonatorProps> = ({
  matchId,
  crowdSnapshot
}) => {
  const [isCheering, setIsCheering] = useState(false);
  const [localCheers, setLocalCheers] = useState(0);
  const cheerIntervalRef = useRef<any>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const decibels = crowdSnapshot?.currentDecibels || 94;
  const peak = crowdSnapshot?.peakDecibels || 118.4;
  const totalCheers = (crowdSnapshot?.cheerCountTotal || 48290) + localCheers;
  const hypeLevel = crowdSnapshot?.hypeLevel || 'HYPED';

  const startCheering = () => {
    setIsCheering(true);
    soundSynth.playCheerPulse(1.5);
    wsClient.sendCheer(matchId, 2.0);
    setLocalCheers(prev => prev + 1);

    if (navigator.vibrate) {
      navigator.vibrate([40, 20, 60]);
    }

    cheerIntervalRef.current = setInterval(() => {
      soundSynth.playCheerPulse(1.8);
      wsClient.sendCheer(matchId, 2.5);
      setLocalCheers(prev => prev + 1);
    }, 380);
  };

  const stopCheering = () => {
    setIsCheering(false);
    if (cheerIntervalRef.current) {
      clearInterval(cheerIntervalRef.current);
      cheerIntervalRef.current = null;
    }
  };

  // Dynamic Spectrum Audio Waveform
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let t = 0;

    const render = () => {
      t += 0.08;
      const w = (canvas.width = canvas.parentElement?.clientWidth || 220);
      const h = (canvas.height = 36);

      ctx.clearRect(0, 0, w, h);

      const bars = 20;
      const barW = (w / bars) - 2;

      for (let i = 0; i < bars; i++) {
        const factor = Math.sin(t + i * 0.45) * 0.5 + 0.5;
        const cheerBoost = isCheering ? 1.5 : 1.0;
        const barH = (factor * (h * 0.65) + (decibels / 120) * (h * 0.35)) * cheerBoost;

        const x = i * (barW + 2);
        const y = h - Math.min(h, barH);

        const grad = ctx.createLinearGradient(0, y, 0, h);
        if (decibels > 105) {
          grad.addColorStop(0, '#ff0055');
          grad.addColorStop(1, '#ffb703');
        } else {
          grad.addColorStop(0, '#00f0ff');
          grad.addColorStop(1, '#9d4edd');
        }

        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barW, Math.min(h, barH));
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [decibels, isCheering]);

  return (
    <div className={`glass-panel p-4 border transition-all duration-300 ${
      isCheering ? 'glass-card-glow-rose' : 'border-white/10'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Volume2 className="w-3.5 h-3.5" />
          </div>
          <div>
            <h4 className="text-xs font-display font-bold text-white">
              CROWD DECIBEL RESONATOR
            </h4>
            <div className="text-[10px] text-slate-400 font-mono">
              Peak: <span className="text-amber-300 font-bold">{peak} dB</span>
            </div>
          </div>
        </div>

        <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold tracking-wider ${
          decibels > 105 
            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse' 
            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
        }`}>
          {hypeLevel}
        </span>
      </div>

      {/* Meter Display & Waveform */}
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-mono font-black text-white">
            {decibels}
          </span>
          <span className="text-[11px] font-mono text-slate-400 font-bold">dB</span>
        </div>

        <div className="flex-1 max-w-[180px]">
          <canvas ref={canvasRef} className="w-full h-8 block" />
        </div>
      </div>

      {/* Interactive Cheer Button */}
      <button
        onMouseDown={startCheering}
        onMouseUp={stopCheering}
        onMouseLeave={stopCheering}
        onTouchStart={startCheering}
        onTouchEnd={stopCheering}
        className={`w-full py-2.5 px-4 rounded-xl font-display text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-all select-none cursor-pointer ${
          isCheering
            ? 'btn-primary-ember shadow-[0_0_25px_rgba(255,0,85,0.7)] scale-98'
            : 'btn-primary-cyan'
        }`}
      >
        <Flame className={`w-4 h-4 ${isCheering ? 'animate-bounce' : ''}`} />
        <span>{isCheering ? 'CHEERING WITH ARENA! 🔥' : 'HOLD TO CHEER ARENA ⚡'}</span>
      </button>

      <div className="flex items-center justify-between mt-2 text-[10px] font-mono text-slate-400">
        <span>Cheers: <span className="text-cyan-300 font-bold">{totalCheers.toLocaleString()}</span></span>
        <span>Stadium Haptic: <span className="text-emerald-400">ONLINE</span></span>
      </div>
    </div>
  );
};
