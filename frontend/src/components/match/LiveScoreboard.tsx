import React from 'react';
import { MatchInfo } from '../../types';

interface LiveScoreboardProps {
  match: MatchInfo;
}

export const LiveScoreboard: React.FC<LiveScoreboardProps> = ({ match }) => {
  const isCricket = match.sport === 'CRICKET';
  const isFootball = match.sport === 'FOOTBALL';
  const isBasketball = match.sport === 'BASKETBALL';

  return (
    <div className="w-full glass-panel p-3.5 border border-white/10 shadow-xl overflow-hidden">
      
      {/* Row 1: Teams & Live Scores */}
      <div className="flex items-center justify-between pb-3 border-b border-white/5">
        
        {/* Home Team */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center font-display font-black text-cyan-300 text-xs">
            {match.homeTeam.slice(0, 3).toUpperCase()}
          </div>
          <div>
            <div className="text-xs font-display font-bold text-white">
              {match.homeTeam}
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg sm:text-xl font-mono font-black text-cyan-300 tracking-tight">
                {match.homeScore.split('(')[0].trim()}
              </span>
              {match.homeScore.includes('(') && (
                <span className="text-[11px] text-slate-400 font-mono">
                  ({match.homeScore.split('(')[1]}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* VS / Clock */}
        <div className="flex flex-col items-center px-2">
          <span className="text-[9px] font-mono text-slate-500 font-bold uppercase">VS</span>
          <span className="text-[10px] font-mono font-bold text-amber-300 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
            {match.gameClock}
          </span>
        </div>

        {/* Away Team */}
        <div className="flex items-center gap-2.5 text-right">
          <div>
            <div className="text-xs font-display font-bold text-white">
              {match.awayTeam}
            </div>
            <div className="flex items-baseline gap-1.5 justify-end">
              <span className="text-lg sm:text-xl font-mono font-black text-purple-300 tracking-tight">
                {match.awayScore.split('(')[0].trim()}
              </span>
              {match.awayScore.includes('(') && (
                <span className="text-[11px] text-slate-400 font-mono">
                  ({match.awayScore.split('(')[1]}
                </span>
              )}
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-display font-black text-purple-300 text-xs">
            {match.awayTeam.slice(0, 3).toUpperCase()}
          </div>
        </div>

      </div>

      {/* Row 2: Live Metrics Chips & Win Probability */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2.5 text-xs font-mono">
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          {isCricket && (
            <>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">Batting:</span> <span className="text-cyan-300 font-bold">{match.metadata?.batsmanStriker || 'V. Kohli 78*'}</span>
              </span>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">Bowler:</span> <span className="text-rose-400 font-bold">{match.metadata?.bowler || 'M. Starc 1/34'}</span>
              </span>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">CRR:</span> <span className="text-amber-300 font-bold">{match.metadata?.crr || '10.41'}</span>
              </span>
            </>
          )}

          {isFootball && (
            <>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">xG:</span> <span className="text-cyan-300 font-bold">{match.metadata?.xGHome || '2.14'}</span> - <span className="text-purple-300 font-bold">{match.metadata?.xGAway || '1.88'}</span>
              </span>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">Possession:</span> <span className="text-emerald-400 font-bold">{match.metadata?.possessionHome || 64}%</span>
              </span>
            </>
          )}

          {isBasketball && (
            <>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">Shot Clock:</span> <span className="text-rose-400 font-bold">{match.metadata?.shotClock || '14s'}</span>
              </span>
              <span className="px-2 py-1 rounded-lg bg-black/40 border border-white/5 text-slate-300">
                <span className="text-slate-400">Top Scorer:</span> <span className="text-amber-300 font-bold">{match.metadata?.topScorer || 'L. James 34 PTS'}</span>
              </span>
            </>
          )}
        </div>

        {/* Win Probability */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-black/50 border border-white/5 text-[10px]">
          <span className="text-cyan-300 font-bold">{match.winProbabilityHome}%</span>
          <div className="w-16 h-1 rounded-full bg-purple-950 overflow-hidden flex">
            <div
              className="h-full bg-cyan-400"
              style={{ width: `${match.winProbabilityHome}%` }}
            />
          </div>
          <span className="text-purple-300 font-bold">{100 - match.winProbabilityHome}%</span>
        </div>
      </div>

    </div>
  );
};
