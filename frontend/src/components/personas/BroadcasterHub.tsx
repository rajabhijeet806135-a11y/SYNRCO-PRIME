import React, { useState } from 'react';
import { Radio, Code2, DollarSign, Activity, Check, Copy, ExternalLink, Sparkles } from 'lucide-react';
import { MatchInfo, SponsoredMoment } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface BroadcasterHubProps {
  match: MatchInfo;
  sponsors: SponsoredMoment[];
  onTriggerSponsor: (sponsor: SponsoredMoment) => void;
}

export const BroadcasterHub: React.FC<BroadcasterHubProps> = ({
  match,
  sponsors,
  onTriggerSponsor
}) => {
  const [copiedCode, setCopiedCode] = useState(false);
  const [activeSponsorKey, setActiveSponsorKey] = useState<string | null>(null);

  const embedSnippet = `<script src="https://cdn.syncroprime.io/sdk/v2.4/syncro-prime.min.js"></script>
<syncro-prime-overlay
  match-id="${match.id}"
  theme="obsidian-space"
  persona-mode="dynamic-ai"
  cqrs-endpoint="wss://gateway.syncroprime.io/ws"
  sponsored-gamification="true">
</syncro-prime-overlay>`;

  const copyEmbedCode = () => {
    navigator.clipboard.writeText(embedSnippet);
    soundSynth.playCoinChime();
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2500);
  };

  const handleInjectSponsor = (sp: SponsoredMoment) => {
    soundSynth.playAlertSound();
    setActiveSponsorKey(sp.campaignKey);
    onTriggerSponsor(sp);
  };

  return (
    <div className="space-y-4 animate-fade-in">
      
      {/* Broadcaster B2B Command Card */}
      <div className="cosmic-glass p-4 border border-blue-500/40 shadow-[0_0_30px_rgba(58,134,255,0.15)]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/40">
              <Radio className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-bold font-display text-white">
                BROADCASTER & OTT EMBEDDABLE SDK PORTAL
              </h3>
              <p className="text-[10px] text-blue-300/80 font-mono">
                Hotstar • ESPN+ • DAZN • Peacock • Zero-Load CQRS Bus
              </p>
            </div>
          </div>

          <span className="text-[10px] px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 font-mono font-bold">
            1.2M LIVE CCU SIMULATED
          </span>
        </div>

        {/* Broadcaster KPI Analytics Matrix */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-xs font-mono">
          <div className="p-2.5 rounded-xl bg-slate-900/70 border border-white/10">
            <div className="text-[10px] text-slate-400">DWELL TIME UPLIFT</div>
            <div className="text-base font-black font-display text-cyan-300 mt-0.5">+42.6%</div>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-900/70 border border-white/10">
            <div className="text-[10px] text-slate-400">VOTE INGEST LATENCY</div>
            <div className="text-base font-black font-display text-emerald-400 mt-0.5">&lt; 18ms</div>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-900/70 border border-white/10">
            <div className="text-[10px] text-slate-400">SPONSOR CPM SURGE</div>
            <div className="text-base font-black font-display text-amber-300 mt-0.5">3.4x ROI</div>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-900/70 border border-white/10">
            <div className="text-[10px] text-slate-400">BACKEND LOAD SPIKE</div>
            <div className="text-base font-black font-display text-blue-300 mt-0.5">0.0% (CQRS)</div>
          </div>
        </div>

        {/* Sponsored Moment Injector */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 mb-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold font-display text-white flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-amber-400" />
              IN-STREAM SPONSORED GAMIFICATION INJECTOR
            </span>
            <span className="text-[10px] font-mono text-slate-400">One-Click Broadcaster Dispatch</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {sponsors.map((sp) => {
              const isTriggered = activeSponsorKey === sp.campaignKey;
              return (
                <button
                  key={sp.campaignKey}
                  onClick={() => handleInjectSponsor(sp)}
                  className={`p-2.5 rounded-xl border text-left transition-all ${
                    isTriggered
                      ? 'bg-amber-500/20 border-amber-400 text-white shadow-[0_0_15px_rgba(255,183,3,0.4)]'
                      : 'bg-slate-950/60 border-white/10 text-slate-300 hover:border-blue-400/40 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="text-xs font-black font-display text-amber-300 flex items-center justify-between">
                    <span>{sp.sponsorLogo}</span>
                    <span className="text-[10px] font-mono text-emerald-400">+{sp.rewardSyncTokens} $SYNC</span>
                  </div>
                  <div className="text-[11px] font-bold text-white mt-1 line-clamp-1">{sp.sponsorName}</div>
                  <p className="text-[10px] text-slate-400 line-clamp-2 mt-0.5">{sp.challengeTitle}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Drop-In SDK Code Generator */}
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/10 text-xs font-mono">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="flex items-center gap-1.5 text-cyan-300 font-bold font-display">
              <Code2 className="w-4 h-4" />
              1-LINE DROP-IN SDK INTEGRATION
            </span>
            <button
              onClick={copyEmbedCode}
              className="flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 transition-all"
            >
              {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedCode ? 'COPIED TO CLIPBOARD' : 'COPY SDK SNIPPET'}</span>
            </button>
          </div>

          <pre className="p-2.5 rounded-lg bg-black/60 text-[11px] text-slate-300 overflow-x-auto font-mono leading-relaxed border border-white/5">
            <code>{embedSnippet}</code>
          </pre>
        </div>

      </div>

    </div>
  );
};
