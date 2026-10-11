import React, { useState } from 'react';
import { Lock, Unlock, Sparkles, Coins, Video, Mic, Award, ShoppingBag, Check } from 'lucide-react';
import { UserProfile } from '../../types';
import { soundSynth } from '../../services/audioSynth';
import confetti from 'canvas-confetti';

interface FanRewardsVaultProps {
  user: UserProfile;
  onRedeemPerk: (cost: number, perkName: string) => void;
  onClose: () => void;
}

interface VaultPerk {
  id: string;
  title: string;
  description: string;
  cost: number;
  icon: React.ReactNode;
  tierRequired: 'Bronze' | 'Silver' | 'Gold' | 'Diamond';
}

export const FanRewardsVault: React.FC<FanRewardsVaultProps> = ({
  user,
  onRedeemPerk,
  onClose
}) => {
  const [unlockedPerks, setUnlockedPerks] = useState<string[]>(['perk_cam_pov']);

  const perks: VaultPerk[] = [
    {
      id: 'perk_cam_pov',
      title: 'VIP 4K Athlete POV Cam Access',
      description: 'Stream directly through helmet & jersey cameras with real-time biometric telemetry.',
      cost: 400,
      icon: <Video className="w-5 h-5 text-cyan-400" />,
      tierRequired: 'Bronze'
    },
    {
      id: 'perk_ref_mic',
      title: 'Umpire / Referee Live Mic Stream',
      description: 'Hear unedited on-pitch communication during DRS reviews and VAR penalty deliberations.',
      cost: 750,
      icon: <Mic className="w-5 h-5 text-purple-400" />,
      tierRequired: 'Silver'
    },
    {
      id: 'perk_holo_badge',
      title: 'Cosmic 2026 World Cup Hologram Badge',
      description: 'Exclusive verifiable digital collectible showcasing your top streak record.',
      cost: 300,
      icon: <Award className="w-5 h-5 text-amber-400" />,
      tierRequired: 'Bronze'
    },
    {
      id: 'perk_fast_pass',
      title: 'Broadcaster Fast-Pass & 25% Merch Pass',
      description: 'Skip stream buffer queues, unlock 60FPS enhanced bitrate and get store discounts.',
      cost: 1200,
      icon: <ShoppingBag className="w-5 h-5 text-rose-400" />,
      tierRequired: 'Gold'
    }
  ];

  const handleUnlock = (perk: VaultPerk) => {
    if (user.syncTokens < perk.cost) {
      alert('Insufficient $SYNC Tokens! Participate in live stoppage predictions to earn more.');
      return;
    }

    soundSynth.playWinFanfare();
    setUnlockedPerks((prev) => [...prev, perk.id]);
    onRedeemPerk(perk.cost, perk.title);

    confetti({
      particleCount: 70,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#ffd700', '#00f0ff', '#ff0055']
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-2xl cosmic-glass-thick p-5 sm:p-6 border border-amber-500/50 shadow-[0_0_50px_rgba(255,183,3,0.3)] relative">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/40">
              <Sparkles className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-black font-display text-white">
                SYNCRO DIGITAL REWARDS VAULT
              </h2>
              <p className="text-xs text-amber-300/80 font-mono">
                Redeem $SYNC Tokens for VIP Broadcast Streams & Collectibles
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold font-mono"
          >
            ✕
          </button>
        </div>

        {/* User Balance & Tier Tracker */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between mb-4 text-xs font-mono">
          <div className="flex items-center gap-2">
            <Coins className="w-4 h-4 text-amber-400" />
            <span className="text-slate-300">Your Balance:</span>
            <span className="font-bold text-amber-300 font-display text-base">
              {user.syncTokens.toLocaleString()} $SYNC
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Status Tier:</span>
            <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold font-display">
              {user.tier} Tier (Level {user.level})
            </span>
          </div>
        </div>

        {/* Perks Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-1">
          {perks.map((p) => {
            const isUnlocked = unlockedPerks.includes(p.id);
            const canAfford = user.syncTokens >= p.cost;

            return (
              <div
                key={p.id}
                className={`p-3.5 rounded-xl border flex flex-col justify-between transition-all ${
                  isUnlocked
                    ? 'bg-emerald-950/30 border-emerald-500/40 shadow-[0_0_15px_rgba(0,255,136,0.15)]'
                    : 'bg-slate-900/60 border-white/10 hover:border-white/20'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                      {p.icon}
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-300">
                      Requires {p.tierRequired}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold font-display text-white mb-1">
                    {p.title}
                  </h4>
                  <p className="text-[11px] text-slate-400 font-sans leading-relaxed mb-3">
                    {p.description}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/10">
                  <span className="text-xs font-bold font-display text-amber-300 flex items-center gap-1">
                    <Coins className="w-3.5 h-3.5 text-amber-400" />
                    {p.cost} $SYNC
                  </span>

                  {isUnlocked ? (
                    <span className="flex items-center gap-1 text-[11px] font-bold font-mono text-emerald-400">
                      <Check className="w-3.5 h-3.5" />
                      UNLOCKED
                    </span>
                  ) : (
                    <button
                      onClick={() => handleUnlock(p)}
                      disabled={!canAfford}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold font-display transition-all ${
                        canAfford
                          ? 'btn-neon-gold scale-100 hover:scale-105'
                          : 'bg-white/5 text-slate-500 border border-white/5 cursor-not-allowed'
                      }`}
                    >
                      {canAfford ? 'Redeem' : 'Locked'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
};
