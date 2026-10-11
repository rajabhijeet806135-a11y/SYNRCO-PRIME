import React, { useState } from 'react';
import { MapPin, Ticket, QrCode, WifiOff, Sparkles, Smartphone, Check } from 'lucide-react';
import { MatchInfo } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface StadiumExperienceHubProps {
  match: MatchInfo;
  isOnline: boolean;
}

export const StadiumExperienceHub: React.FC<StadiumExperienceHubProps> = ({
  match,
  isOnline
}) => {
  const [claimedVoucher, setClaimedVoucher] = useState(false);

  const handleClaim = () => {
    soundSynth.playCoinChime();
    setClaimedVoucher(true);
  };

  return (
    <div className="space-y-4 animate-fade-in">
      
      {/* Stadium In-Venue Cockpit Card */}
      <div className="cosmic-glass p-4 border border-emerald-500/40 shadow-[0_0_30px_rgba(0,255,136,0.15)]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              <MapPin className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-bold font-display text-white">
                IN-STADIUM VENUE EXPERIENCE
              </h3>
              <p className="text-[10px] text-emerald-300/80 font-mono">
                {match.venue} • Section B, Row 12, Seat 44
              </p>
            </div>
          </div>

          <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono font-bold">
            SEAT SYNC: CONNECTED
          </span>
        </div>

        {/* Big-Screen Hawkeye / VAR Stadium Screen Feed */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 mb-3 text-xs font-mono">
          <div className="flex items-center justify-between text-slate-300 mb-2">
            <span className="font-bold font-display text-emerald-300 flex items-center gap-1.5">
              <Smartphone className="w-3.5 h-3.5" />
              STADIUM AR HAWKEYE FEED
            </span>
            <span className="text-slate-400 text-[10px]">ULTRA-LOW LATENCY (&lt;15ms)</span>
          </div>
          <p className="text-slate-300 font-sans text-xs">
            Look up at the North Stadium screen: High-frequency 3D ball trajectory is synchronized with your phone vibration.
          </p>
        </div>

        {/* Flash Concession Discount Card during match pause */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/40 to-slate-900 border border-emerald-500/40 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              <Ticket className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold font-display text-white">
                  20% OFF CONCESSIONS & MERCH
                </span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-500 text-white font-mono font-bold">
                  DURING VAR PAUSE
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                Valid at all Gate 4 & 6 stadium food kiosks for the next 8 minutes.
              </p>
            </div>
          </div>

          <button
            onClick={handleClaim}
            disabled={claimedVoucher}
            className={`px-4 py-2 rounded-xl text-xs font-bold font-display flex items-center gap-1.5 whitespace-nowrap transition-all ${
              claimedVoucher
                ? 'bg-emerald-500 text-black shadow-[0_0_15px_#00ff88]'
                : 'btn-neon-cyan'
            }`}
          >
            {claimedVoucher ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>VOUCHER ACTIVE (CODE #8824)</span>
              </>
            ) : (
              <>
                <QrCode className="w-3.5 h-3.5" />
                <span>CLAIM VOUCHER</span>
              </>
            )}
          </button>
        </div>

        {/* Offline / Stadium 5G Tolerance Banner */}
        <div className="mt-3 p-3 rounded-xl bg-slate-900/60 border border-white/10 text-xs font-mono text-slate-400 flex items-center justify-between">
          <span>Stadium 5G Congestion Protection: <span className="text-emerald-400 font-bold">ENABLED</span></span>
          <span className="text-slate-300">IndexedDB Offline Queue: <span className="text-cyan-400">0 queued</span></span>
        </div>

      </div>

    </div>
  );
};
