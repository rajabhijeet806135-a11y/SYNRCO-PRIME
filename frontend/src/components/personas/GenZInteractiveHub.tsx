import React, { useState, useEffect } from 'react';
import { Zap, Clock, Sparkles, Heart, Check, Flame } from 'lucide-react';
import { MatchInfo, ContextualPrediction, UserProfile } from '../../types';
import { soundSynth } from '../../services/audioSynth';
import confetti from 'canvas-confetti';

interface GenZInteractiveHubProps {
  match: MatchInfo;
  user: UserProfile;
  onVote: (predictionId: string, option: string, stake: number) => void;
  activePrediction: ContextualPrediction | null;
}

export const GenZInteractiveHub: React.FC<GenZInteractiveHubProps> = ({
  match,
  user,
  onVote,
  activePrediction
}) => {
  const [selectedStake, setSelectedStake] = useState<number>(50);
  const [votedOption, setVotedOption] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState<number>(15);
  const [floatingEmojis, setFloatingEmojis] = useState<{ id: number; emoji: string; x: number }[]>([]);

  const emojis = ['🔥', '⚡', '🚀', '👑', '🐐', '💥'];

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          soundSynth.playCountdownTick(true);
          return 15;
        }
        if (prev <= 4) {
          soundSynth.playCountdownTick(false);
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleEmojiClick = (emoji: string) => {
    soundSynth.playCoinChime();
    const id = Date.now() + Math.random();
    setFloatingEmojis((prev) => [...prev, { id, emoji, x: Math.random() * 80 + 10 }]);
    setTimeout(() => {
      setFloatingEmojis((prev) => prev.filter((item) => item.id !== id));
    }, 1800);
  };

  const handleVoteSubmit = (option: string) => {
    setVotedOption(option);
    soundSynth.playCoinChime();
    onVote(activePrediction?.id || 'pred_rapid_1', option, selectedStake);

    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.7 },
      colors: ['#ff0055', '#00f0ff', '#ffd700']
    });
  };

  const defaultQuestion = match.sport === 'CRICKET'
    ? 'Next Delivery: Will Kohli score a boundary on 17.5?'
    : match.sport === 'FOOTBALL'
    ? 'VAR Verdict: Will penalty kick be awarded?'
    : 'Final 24s: Will LeBron convert the clutch stepback?';

  const defaultOptions = match.sport === 'CRICKET'
    ? [
        { label: 'Boundary (4 or 6) 🚀', odds: 2.40, pct: 64 },
        { label: 'Dot Ball 🛡️', odds: 1.85, pct: 18 },
        { label: 'Wicket Out 💥', odds: 4.50, pct: 10 },
        { label: '1 or 2 Runs ⚡', odds: 1.50, pct: 8 }
      ]
    : match.sport === 'FOOTBALL'
    ? [
        { label: 'Penalty Awarded ⚽', odds: 1.65, pct: 72 },
        { label: 'Play On / No Foul 🚫', odds: 2.25, pct: 28 }
      ]
    : [
        { label: 'Clutch 3-Pointer 🔥', odds: 2.10, pct: 58 },
        { label: 'Drive & Layup 🏀', odds: 1.75, pct: 42 }
      ];

  return (
    <div className="space-y-3 relative overflow-hidden">
      
      {/* Floating Emojis */}
      <div className="absolute inset-0 pointer-events-none z-30">
        {floatingEmojis.map((fe) => (
          <div
            key={fe.id}
            className="absolute bottom-6 text-2xl animate-fade-in"
            style={{
              left: `${fe.x}%`,
              animation: 'floatUp 1.6s ease-out forwards'
            }}
          >
            {fe.emoji}
          </div>
        ))}
      </div>

      <style>{`
        @keyframes floatUp {
          0% { transform: translateY(0) scale(0.9); opacity: 1; }
          100% { transform: translateY(-140px) scale(1.3); opacity: 0; }
        }
      `}</style>

      {/* 15s Rapid Micro-Challenge Card */}
      <div className="glass-panel p-4 border border-rose-500/40 shadow-[0_0_25px_rgba(255,0,85,0.12)]">
        
        {/* Top Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30">
              <Zap className="w-4 h-4 animate-bounce" />
            </div>
            <div>
              <h4 className="text-xs font-display font-bold text-white flex items-center gap-1.5">
                <span>15s Rapid Micro-Challenge</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 font-mono font-bold">
                  2x Multiplier
                </span>
              </h4>
              <p className="text-[10px] text-slate-400 font-mono">
                Instant Settlement & Payout
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/15 border border-rose-500/40 text-rose-300 font-mono font-bold text-xs">
            <Clock className="w-3.5 h-3.5" />
            <span>00:{timeLeft < 10 ? `0${timeLeft}` : timeLeft}s</span>
          </div>
        </div>

        {/* Question Title */}
        <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 mb-3">
          <p className="text-xs sm:text-sm font-display font-bold text-white">
            {activePrediction?.question || defaultQuestion}
          </p>
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
          {defaultOptions.map((opt) => {
            const isChosen = votedOption === opt.label;
            return (
              <button
                key={opt.label}
                onClick={() => handleVoteSubmit(opt.label)}
                className={`p-2.5 rounded-xl border text-left transition-all select-none cursor-pointer flex flex-col justify-between ${
                  isChosen
                    ? 'bg-rose-500/25 border-rose-400 shadow-[0_0_20px_rgba(255,0,85,0.4)]'
                    : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-cyan-400/40'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="font-display font-bold text-xs text-white flex items-center gap-1">
                    {isChosen && <Check className="w-3.5 h-3.5 text-rose-400" />}
                    {opt.label}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-[11px] font-bold">
                    {opt.odds.toFixed(2)}x
                  </span>
                </div>

                {/* Consensus Progress Bar */}
                <div className="w-full flex items-center gap-2 text-[10px] text-slate-400 font-mono">
                  <div className="flex-1 h-1 rounded-full bg-white/10 overflow-hidden">
                    <div 
                      className={`h-full ${isChosen ? 'bg-rose-400' : 'bg-cyan-400'}`} 
                      style={{ width: `${opt.pct}%` }} 
                    />
                  </div>
                  <span>{opt.pct}% voted</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Stake Chips & Potential Win */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/10 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400 font-mono text-[11px]">Stake:</span>
            {[25, 50, 100, 250].map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStake(st)}
                className={`px-2 py-0.5 rounded-lg font-mono font-bold text-[11px] transition-all cursor-pointer ${
                  selectedStake === st
                    ? 'bg-amber-400 text-black shadow-[0_0_8px_#ffd700]'
                    : 'bg-white/5 text-slate-300 hover:bg-white/10'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="font-mono text-slate-300 text-[11px]">
            Est. Return: <span className="font-bold text-amber-300">+{Math.round(selectedStake * 2.4)} $SYNC</span>
          </div>
        </div>

      </div>

      {/* Floating Reaction Bar */}
      <div className="glass-panel p-2.5 flex items-center justify-between border border-white/10">
        <span className="text-xs font-display font-bold text-slate-300 flex items-center gap-1.5">
          <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
          <span>Hype Pulse:</span>
        </span>

        <div className="flex items-center gap-1.5">
          {emojis.map((em) => (
            <button
              key={em}
              onClick={() => handleEmojiClick(em)}
              className="text-lg p-1.5 rounded-lg bg-white/5 hover:bg-rose-500/20 border border-white/10 hover:border-rose-400 hover:scale-120 active:scale-95 transition-all cursor-pointer"
            >
              {em}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
};
