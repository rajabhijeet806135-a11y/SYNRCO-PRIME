import React, { useState } from 'react';
import { Trophy, Flame, Users } from 'lucide-react';
import { LeaderboardUser, ClanInfo, UserProfile } from '../../types';

interface LeaderboardPanelProps {
  users: LeaderboardUser[];
  clans: ClanInfo[];
  currentUser: UserProfile;
}

export const LeaderboardPanel: React.FC<LeaderboardPanelProps> = ({
  users,
  clans,
  currentUser
}) => {
  const [tab, setTab] = useState<'GLOBAL' | 'CLANS'>('GLOBAL');

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Diamond': return 'text-cyan-400 border-cyan-400/40 bg-cyan-500/10';
      case 'Gold': return 'text-amber-400 border-amber-400/40 bg-amber-500/10';
      case 'Silver': return 'text-slate-300 border-slate-400/40 bg-slate-500/10';
      default: return 'text-amber-600 border-amber-700/40 bg-amber-900/10';
    }
  };

  return (
    <div className="glass-panel p-4 border border-white/10 shadow-xl">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Trophy className="w-3.5 h-3.5" />
          </div>
          <div>
            <h4 className="text-xs font-display font-bold text-white">
              CQRS LIVE LEADERBOARD
            </h4>
            <p className="text-[10px] text-slate-400 font-mono">
              Real-Time Rank Aggregation
            </p>
          </div>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center gap-1 p-0.5 rounded-lg bg-black/40 border border-white/10">
          <button
            onClick={() => setTab('GLOBAL')}
            className={`px-2 py-0.5 rounded-md text-[11px] font-display font-bold transition-all cursor-pointer ${
              tab === 'GLOBAL'
                ? 'bg-amber-400 text-black shadow-[0_0_8px_#ffd700]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Fans
          </button>
          <button
            onClick={() => setTab('CLANS')}
            className={`px-2 py-0.5 rounded-md text-[11px] font-display font-bold transition-all cursor-pointer ${
              tab === 'CLANS'
                ? 'bg-amber-400 text-black shadow-[0_0_8px_#ffd700]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Clans
          </button>
        </div>
      </div>

      {/* List */}
      {tab === 'GLOBAL' ? (
        <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
          {users.map((u) => {
            const isMe = u.userId === currentUser.userId;
            return (
              <div
                key={u.userId}
                className={`p-2 rounded-xl border flex items-center justify-between transition-all ${
                  isMe
                    ? 'bg-cyan-500/15 border-cyan-400/50 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                    : 'bg-black/30 border-white/5 hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-4 text-center font-mono font-bold text-xs ${
                    u.rank === 1 ? 'text-amber-400 font-black' : u.rank === 2 ? 'text-slate-300' : u.rank === 3 ? 'text-amber-600' : 'text-slate-500'
                  }`}>
                    #{u.rank}
                  </span>
                  <span className="text-sm">{u.avatar}</span>
                  <div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-display font-bold text-white">{u.username}</span>
                      {isMe && <span className="text-[8px] px-1 rounded bg-cyan-400 text-black font-mono font-bold">YOU</span>}
                    </div>
                    <div className="text-[9px] text-slate-400 font-mono">
                      {u.persona}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-right">
                  <div className="flex items-center gap-0.5 text-[11px] font-mono text-rose-400 font-bold">
                    <Flame className="w-3 h-3 fill-rose-500" />
                    <span>{u.streak}x</span>
                  </div>
                  <div>
                    <div className="text-xs font-mono font-bold text-amber-300">
                      {u.score.toLocaleString()} XP
                    </div>
                    <span className={`text-[8px] px-1 py-0.2 rounded font-mono border font-bold ${getTierColor(u.tier)}`}>
                      {u.tier}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
          {clans.map((c) => (
            <div
              key={c.id}
              className="p-2 rounded-xl bg-black/30 border border-white/5 flex items-center justify-between hover:bg-white/5 transition-all"
            >
              <div className="flex items-center gap-2">
                <span className="w-4 text-center font-mono font-bold text-xs text-amber-400">
                  #{c.rank}
                </span>
                <span className="text-base">{c.badge}</span>
                <div>
                  <div className="text-xs font-display font-bold text-white">{c.name}</div>
                  <div className="text-[9px] text-slate-400 font-mono flex items-center gap-1">
                    <Users className="w-2.5 h-2.5" />
                    <span>{c.memberCount.toLocaleString()} members</span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="text-xs font-mono font-bold text-amber-300">
                  {c.totalXp.toLocaleString()} XP
                </div>
                <span className="text-[9px] text-emerald-400 font-mono">
                  {c.sport}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
