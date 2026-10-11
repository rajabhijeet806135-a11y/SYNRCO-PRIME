import React, { useState } from 'react';
import { 
  Flame, 
  Coins, 
  Sparkles, 
  History, 
  Radio, 
  ChevronDown,
  Volume2,
  VolumeX,
  Wifi
} from 'lucide-react';
import { MatchInfo, SportType, UserProfile } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface TopNavigationProps {
  matches: MatchInfo[];
  selectedMatch: MatchInfo;
  onSelectMatch: (match: MatchInfo) => void;
  selectedSport: SportType | 'ALL';
  onSelectSport: (sport: SportType | 'ALL') => void;
  user: UserProfile;
  onOpenQuiz: () => void;
  onOpenHistorical: () => void;
  onOpenVault: () => void;
  isOnline: boolean;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  matches,
  selectedMatch,
  onSelectMatch,
  selectedSport,
  onSelectSport,
  user,
  onOpenQuiz,
  onOpenHistorical,
  onOpenVault,
  isOnline
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isMuted, setIsMuted] = useState(soundSynth.getIsMuted());

  const toggleSound = () => {
    const next = !isMuted;
    setIsMuted(next);
    soundSynth.setMuted(next);
    if (!next) soundSynth.playCoinChime();
  };

  const sports: { id: SportType | 'ALL'; label: string; icon: string }[] = [
    { id: 'ALL', label: 'All Arenas', icon: '⚡' },
    { id: 'CRICKET', label: 'Cricket', icon: '🏏' },
    { id: 'FOOTBALL', label: 'Football', icon: '⚽' },
    { id: 'BASKETBALL', label: 'Basketball', icon: '🏀' }
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#080a14]/90 backdrop-blur-xl border-b border-white/10 px-4 sm:px-6 py-2.5">
      <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-4">
        
        {/* Brand & Match Selector */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.4)]">
              <Radio className="w-4 h-4 text-black animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-brand font-black text-sm sm:text-base tracking-wider text-white">
                  SYNCRO<span className="text-cyan-400">PRIME</span>
                </span>
                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  AI 2.4
                </span>
              </div>
            </div>
          </div>

          <div className="h-5 w-[1px] bg-white/10 hidden sm:block" />

          {/* Match Dropdown */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 transition-all"
            >
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
              <span className="font-display font-bold">
                {selectedMatch.homeTeam} vs {selectedMatch.awayTeam}
              </span>
              <span className="text-[10px] text-amber-400 font-mono hidden md:inline">
                ({selectedMatch.gameClock})
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 mt-1.5 w-72 bg-[#0c1020] border border-white/15 rounded-xl shadow-2xl p-1.5 z-50">
                <div className="text-[10px] font-mono text-slate-400 px-2 py-1 uppercase tracking-wider">
                  Live Broadcast Matches
                </div>
                {matches.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => {
                      soundSynth.playAlertSound();
                      onSelectMatch(m);
                      setDropdownOpen(false);
                    }}
                    className={`w-full flex items-center justify-between p-2 rounded-lg text-left text-xs transition-all ${
                      selectedMatch.id === m.id
                        ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold'
                        : 'hover:bg-white/5 text-slate-300'
                    }`}
                  >
                    <div>
                      <div className="font-display">{m.homeTeam} vs {m.awayTeam}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{m.sport} • {m.gameClock}</div>
                    </div>
                    <span className="text-[9px] font-mono text-rose-400 bg-rose-500/15 px-1.5 py-0.5 rounded font-bold">
                      LIVE
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center: Sports Filter Pills */}
        <div className="hidden xl:flex items-center gap-1 p-1 rounded-xl bg-black/40 border border-white/5">
          {sports.map((s) => (
            <button
              key={s.id}
              onClick={() => onSelectSport(s.id)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold font-display transition-all cursor-pointer ${
                selectedSport === s.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>{s.icon}</span>
              <span>{s.label}</span>
            </button>
          ))}
        </div>

        {/* Right: Tokens, Streak, Modals */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* CQRS Status */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-[11px] font-mono">
            <Wifi className="w-3 h-3 animate-pulse" />
            <span>CQRS LIVE (18ms)</span>
          </div>

          {/* Tokens Vault Button */}
          <button
            onClick={onOpenVault}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-mono font-bold transition-all shadow-[0_0_12px_rgba(255,183,3,0.15)]"
            title="Open Rewards Vault"
          >
            <Coins className="w-3.5 h-3.5 text-amber-400" />
            <span>{user.syncTokens.toLocaleString()}</span>
            <span className="text-[10px] text-amber-400/70">$SYNC</span>
          </button>

          {/* Streak Flame */}
          <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-mono font-bold streak-flame-anim">
            <Flame className="w-3.5 h-3.5 fill-rose-500 text-rose-400" />
            <span>{user.currentStreak}x</span>
          </div>

          {/* Historical Matrix Button */}
          <button
            onClick={onOpenHistorical}
            title="Head-to-Head Analytics (Dataset 4)"
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white flex items-center justify-center transition-all"
          >
            <History className="w-4 h-4 text-purple-400" />
          </button>

          {/* AI Quiz Button */}
          <button
            onClick={onOpenQuiz}
            title="Calibrate AI Persona"
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white flex items-center justify-center transition-all"
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </button>

          {/* Sound FX Toggle */}
          <button
            onClick={toggleSound}
            title={isMuted ? 'Unmute Audio FX' : 'Mute Audio FX'}
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white flex items-center justify-center transition-all"
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-slate-500" /> : <Volume2 className="w-4 h-4 text-cyan-400 animate-pulse" />}
          </button>
        </div>

      </div>
    </header>
  );
};
