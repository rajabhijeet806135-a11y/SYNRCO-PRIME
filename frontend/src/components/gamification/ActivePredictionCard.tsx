import React, { useState, useEffect } from 'react';
import { Zap, Clock, Coins, ShieldCheck, Flame, Check } from 'lucide-react';
import { ContextualPrediction, UserProfile } from '../../types';
import { soundSynth } from '../../services/audioSynth';
import confetti from 'canvas-confetti';

interface ActivePredictionCardProps {
  prediction: ContextualPrediction;
  user: UserProfile;
  onVote: (predictionId: string, option: string, stake: number) => void;
  onClose?: () => void;
}

export const ActivePredictionCard: React.FC<ActivePredictionCardProps> = ({
  prediction,
  user,
  onVote,
  onClose
}) => {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [stake, setStake] = useState<number>(50);
  const [timeLeft, setTimeLeft] = useState<number>(prediction.windowSeconds || 30);
  const [submitted, setSubmitted] = useState<boolean>(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleSubmitVote = (option: string) => {
    setSelectedOption(option);
    setSubmitted(true);
    soundSynth.playCoinChime();
    onVote(prediction.id, option, stake);

    confetti({
      particleCount: 40,
      spread: 50,
      origin: { y: 0.8 },
      colors: ['#00f0ff', '#9d4edd', '#ffd700']
    });
  };

  const currentOdds = selectedOption ? prediction.odds[selectedOption] || 2.0 : 2.0;
  const potentialPayout = Math.round(stake * currentOdds);

  return (
    <div className="cosmic-glass p-4 sm:p-5 border border-cyan-500/50 shadow-[0_0_35px_rgba(0,240,255,0.25)] relative overflow-hidden">
      
      {/* Top Banner */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
            <Zap className="w-4 h-4 animate-bounce" />
          </div>
          <div>
            <div className="text-xs font-bold font-display text-white">
              {prediction.title}
            </div>
            <div className="text-[10px] text-cyan-300/80 font-mono">
              Event: {prediction.eventType} • Sybil Defense Active
            </div>
          </div>
        </div>

        {/* Countdown Ring */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-mono font-bold text-xs shadow-[0_0_12px_rgba(0,240,255,0.4)]">
          <Clock className="w-3.5 h-3.5 animate-spin-slow" />
          <span>{timeLeft}s</span>
        </div>
      </div>

      {/* Question */}
      <div className="p-3 rounded-xl bg-slate-900/80 border border-white/10 my-3">
        <p className="text-xs sm:text-sm font-bold text-slate-100 font-heading">
          {prediction.question}
        </p>
      </div>

      {/* Prediction Options */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 my-3">
        {prediction.options.map((opt) => {
          const isSelected = selectedOption === opt;
          const odds = prediction.odds[opt] || 2.0;
          return (
            <button
              key={opt}
              disabled={submitted}
              onClick={() => handleSubmitVote(opt)}
              className={`p-3 rounded-xl border text-left flex items-center justify-between transition-all select-none ${
                isSelected
                  ? 'bg-cyan-500/30 border-cyan-400 text-white shadow-[0_0_20px_rgba(0,240,255,0.5)] scale-[1.02]'
                  : submitted
                  ? 'bg-slate-900/40 border-white/5 text-slate-500 cursor-not-allowed'
                  : 'bg-slate-900/60 border-white/10 text-slate-200 hover:bg-white/10 hover:border-cyan-400/50'
              }`}
            >
              <div className="flex items-center gap-2">
                {isSelected && <Check className="w-4 h-4 text-cyan-400" />}
                <span className="font-bold font-display text-xs">{opt}</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-white/10 text-amber-300 font-mono text-xs font-bold">
                {odds}x
              </span>
            </button>
          );
        })}
      </div>

      {/* Stake & Potential Payout Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2.5 border-t border-white/10 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-mono text-[11px]">Stake:</span>
          {[25, 50, 100].map((st) => (
            <button
              key={st}
              disabled={submitted}
              onClick={() => setStake(st)}
              className={`px-2.5 py-1 rounded-lg font-mono font-bold text-xs transition-all ${
                stake === st
                  ? 'bg-amber-400 text-black shadow-[0_0_8px_#ffd700]'
                  : 'bg-white/5 text-slate-300 hover:bg-white/10'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5 font-mono text-slate-300 text-xs">
          <span>Est. Payout:</span>
          <span className="font-bold text-amber-300 font-display text-sm">
            +{potentialPayout} $SYNC
          </span>
        </div>
      </div>

      {submitted && (
        <div className="mt-2.5 p-2 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-center text-xs font-mono font-bold animate-pulse">
          ✓ VOTE RECORDED ATOMICALLY (&lt;24ms) • AWAITING SETTLEMENT
        </div>
      )}

    </div>
  );
};
