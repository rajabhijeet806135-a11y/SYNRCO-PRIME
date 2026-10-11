import React, { useState } from 'react';
import { Brain, Sparkles, BookOpen, ChevronRight, Check } from 'lucide-react';
import { MatchInfo } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface CasualExplainerHubProps {
  match: MatchInfo;
}

export const CasualExplainerHub: React.FC<CasualExplainerHubProps> = ({ match }) => {
  const [selectedPoll, setSelectedPoll] = useState<string | null>(null);

  const isCricket = match.sport === 'CRICKET';
  const isFootball = match.sport === 'FOOTBALL';

  const explanations = isCricket
    ? {
        title: 'DRS Ball-Tracking Review Explained',
        summary: 'Australia appealed that the ball struck Kohli’s pads in line with the stumps. The TV umpire checked Hawkeye ball-tracking: pitching in line, impact in line, but ball is clipping the outer edge of off-stump.',
        verdict: 'Umpire’s Call — On-field decision stands (NOT OUT).'
      }
    : isFootball
    ? {
        title: 'VAR Handball & Penalty Deliberation Explained',
        summary: 'Checking whether the defender’s arm was in an unnatural position extending the body silhouette when blocking the cross.',
        verdict: 'Penalty kick awarded if arm was extended beyond natural posture.'
      }
    : {
        title: 'Clutch Possession & Shot Clock Explained',
        summary: 'With 24 seconds left on the game clock, the offensive team must attempt a shot that hits the rim before the shot clock buzzer.',
        verdict: 'Defensive foul in act of shooting awards two clutch free throws.'
      };

  const glossaryItems = [
    { term: isCricket ? 'DRS Review' : isFootball ? 'VAR' : 'Shot Clock', desc: isCricket ? 'Decision Review System using optical trajectory cameras.' : isFootball ? 'Video Assistant Referee reviewing game-changing calls.' : '24-second timer requiring a shot attempt.' },
    { term: isCricket ? 'Umpire’s Call' : isFootball ? 'Offside Line' : 'Bonus Foul', desc: isCricket ? 'Margin of doubt where on-field verdict stays if impact is borderline.' : isFootball ? 'Semi-automated 3D line drawn from furthest scoring body part.' : 'Shooting free throws on 5+ opponent fouls.' },
    { term: isCricket ? 'Yorker' : isFootball ? 'xG (Expected Goals)' : 'The Paint', desc: isCricket ? 'A fast delivery targeted right at the batsman’s toes.' : isFootball ? 'Statistical quality of a scoring chance (0.0 to 1.0).' : 'The rectangular key area underneath the basket.' }
  ];

  const handlePollVote = (opt: string) => {
    soundSynth.playCoinChime();
    setSelectedPoll(opt);
  };

  return (
    <div className="space-y-3 animate-fade-in">
      
      {/* Plain-English AI Rule Card */}
      <div className="glass-panel p-4 border border-cyan-500/40 shadow-[0_0_25px_rgba(0,240,255,0.12)]">
        <div className="flex items-center gap-2 mb-2.5">
          <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <Brain className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h4 className="text-xs font-display font-bold text-white flex items-center gap-1.5">
              <span>{explanations.title}</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/15 text-cyan-300 font-mono">
                PLAIN ENGLISH
              </span>
            </h4>
            <p className="text-[10px] text-slate-400 font-mono">
              Zero Sports Jargon • AI Context Summary
            </p>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/25 text-slate-200 text-xs leading-relaxed mb-2.5">
          {explanations.summary}
        </div>

        <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 text-xs text-slate-300 flex items-center gap-1.5">
          <span className="text-cyan-400 font-mono font-bold">Rule Impact:</span>
          <span>{explanations.verdict}</span>
        </div>
      </div>

      {/* Casual Viewer 1-Tap Poll */}
      <div className="glass-panel p-3.5 border border-white/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-display font-bold text-white flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Quick 1-Tap Fan Poll
          </span>
          <span className="text-[10px] font-mono text-cyan-300">+50 XP</span>
        </div>

        <p className="text-xs text-slate-200 mb-2.5">
          {isCricket 
            ? 'Did the umpire make the right call on the field?'
            : isFootball 
            ? 'Was this handball unnatural movement?'
            : 'Who had the better offensive drive this quarter?'}
        </p>

        <div className="grid grid-cols-3 gap-1.5">
          {['Right Call', 'Disagree', 'Borderline'].map((opt) => {
            const isSelected = selectedPoll === opt;
            return (
              <button
                key={opt}
                onClick={() => handlePollVote(opt)}
                className={`py-2 px-2.5 rounded-xl border text-xs font-display font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                  isSelected
                    ? 'bg-cyan-500/25 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,240,255,0.4)]'
                    : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10 hover:border-cyan-400/30'
                }`}
              >
                {isSelected && <Check className="w-3 h-3 text-cyan-400" />}
                <span>{opt}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 1-Tap Rule Guide */}
      <div className="glass-panel p-3.5 border border-white/10">
        <div className="flex items-center gap-1.5 mb-2 text-xs font-display font-bold text-slate-300">
          <BookOpen className="w-3.5 h-3.5 text-purple-400" />
          <span>Quick Rule Explainer Cards</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {glossaryItems.map((item) => (
            <div
              key={item.term}
              className="p-2.5 rounded-xl bg-black/40 border border-white/5 text-left"
            >
              <div className="text-xs font-display font-bold text-purple-300 mb-0.5">
                {item.term}
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
