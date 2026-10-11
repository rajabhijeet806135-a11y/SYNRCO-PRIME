import React, { useState } from 'react';
import { History, Database, Flame, Swords, Shield, Target } from 'lucide-react';
import { SportType } from '../../types';

interface HistoricalH2HModalProps {
  onClose: () => void;
}

export const HistoricalH2HModal: React.FC<HistoricalH2HModalProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<SportType>('CRICKET');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-2xl cosmic-glass-thick p-5 sm:p-6 border border-purple-500/50 shadow-[0_0_50px_rgba(157,78,221,0.3)] relative">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/40">
              <History className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-black font-display text-white">
                HISTORICAL HEAD-TO-HEAD MATRICES
              </h3>
              <p className="text-xs text-purple-300/80 font-mono">
                Dataset 4 Telemetry • 5-Year High-Lev Matchup Telemetry
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white flex items-center justify-center text-xs font-mono font-bold"
          >
            ✕
          </button>
        </div>

        {/* Sport Switcher Tabs */}
        <div className="flex items-center gap-2 mb-4 p-1 rounded-xl bg-slate-900/80 border border-white/10">
          {[
            { id: 'CRICKET' as SportType, label: 'Cricket: Kohli vs Starc 🏏' },
            { id: 'FOOTBALL' as SportType, label: 'Football: Haaland vs Courtois ⚽' },
            { id: 'BASKETBALL' as SportType, label: 'Basketball: LeBron vs Curry 🏀' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold font-display transition-all ${
                activeTab === tab.id
                  ? 'bg-purple-500/30 text-purple-200 border border-purple-400/50 shadow-[0_0_12px_rgba(157,78,221,0.3)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dynamic Matchup Content */}
        {activeTab === 'CRICKET' && (
          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between">
              <div className="text-left">
                <div className="text-sm font-black font-display text-cyan-300">VIRAT KOHLI</div>
                <div className="text-[10px] text-slate-400 font-mono">Right-Hand Top Order</div>
              </div>
              <div className="px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 text-xs font-mono font-bold border border-purple-500/40">
                12 T20 MATCHUPS (2021-2026)
              </div>
              <div className="text-right">
                <div className="text-sm font-black font-display text-rose-400">MITCHELL STARC</div>
                <div className="text-[10px] text-slate-400 font-mono">Left-Arm Fast Express</div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">RUNS SCORED</div>
                <div className="text-base font-bold text-white mt-1">114 Runs</div>
                <div className="text-[10px] text-cyan-400">78 Balls Faced</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">STRIKE RATE</div>
                <div className="text-base font-bold text-amber-300 mt-1">146.15</div>
                <div className="text-[10px] text-slate-400">+12% vs Avg</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">DISMISSALS</div>
                <div className="text-base font-bold text-rose-400 mt-1">2 Times</div>
                <div className="text-[10px] text-slate-400">Avg 57.0</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">BOUNDARY %</div>
                <div className="text-base font-bold text-emerald-400 mt-1">21.8%</div>
                <div className="text-[10px] text-slate-400">11 Fours, 4 Sixes</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-purple-950/30 border border-purple-500/30 text-xs font-mono text-slate-300">
              <span className="font-bold text-purple-300">AI Predictive Summary:</span> Kohli scores 1.82 runs/ball when Starc bowls short of length, but strike rate drops to 112 against full swinging deliveries.
            </div>
          </div>
        )}

        {activeTab === 'FOOTBALL' && (
          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between">
              <div className="text-left">
                <div className="text-sm font-black font-display text-cyan-300">ERLING HAALAND</div>
                <div className="text-[10px] text-slate-400 font-mono">Manchester City #9</div>
              </div>
              <div className="px-3 py-1 rounded-lg bg-blue-500/20 text-blue-300 text-xs font-mono font-bold border border-blue-500/40">
                PENALTY & OPEN PLAY H2H
              </div>
              <div className="text-right">
                <div className="text-sm font-black font-display text-purple-300">THIBAUT COURTOIS</div>
                <div className="text-[10px] text-slate-400 font-mono">Real Madrid Goalkeeper</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">PENALTIES FACED</div>
                <div className="text-base font-bold text-white mt-1">4 Spot-Kicks</div>
                <div className="text-[10px] text-cyan-400">3 Converted (75%)</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">PREFERRED SIDE</div>
                <div className="text-base font-bold text-amber-300 mt-1">Bottom Right</div>
                <div className="text-[10px] text-slate-400">118 km/h Exit Velocity</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">SAVES / STOPS</div>
                <div className="text-base font-bold text-rose-400 mt-1">1 Save</div>
                <div className="text-[10px] text-slate-400">UCL 2023 Semis</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'BASKETBALL' && (
          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between">
              <div className="text-left">
                <div className="text-sm font-black font-display text-amber-400">LEBRON JAMES</div>
                <div className="text-[10px] text-slate-400 font-mono">Lakers #23</div>
              </div>
              <div className="px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 text-xs font-mono font-bold border border-amber-500/40">
                CLUTCH 4TH QUARTER H2H
              </div>
              <div className="text-right">
                <div className="text-sm font-black font-display text-blue-400">STEPHEN CURRY</div>
                <div className="text-[10px] text-slate-400 font-mono">Warriors #30</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">FINAL 2-MIN SHOTS</div>
                <div className="text-base font-bold text-white mt-1">LeBron 52.4%</div>
                <div className="text-[10px] text-slate-400">Curry 48.8%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">CLUTCH 3PT %</div>
                <div className="text-base font-bold text-amber-300 mt-1">Curry 43.2%</div>
                <div className="text-[10px] text-slate-400">LeBron 36.1%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/10 text-center">
                <div className="text-[10px] text-slate-400">HEAD-TO-HEAD WINS</div>
                <div className="text-base font-bold text-emerald-400 mt-1">LeBron 23 - 21</div>
                <div className="text-[10px] text-slate-400">44 Total Games</div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
