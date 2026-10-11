import React from 'react';
import { Play, Film, Volume2, Sparkles } from 'lucide-react';
import { AiHighlightClip } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface AiHighlightsDrawerProps {
  highlights: AiHighlightClip[];
  onPlayClip: (clip: AiHighlightClip) => void;
}

export const AiHighlightsDrawer: React.FC<AiHighlightsDrawerProps> = ({
  highlights,
  onPlayClip
}) => {
  const handleClipClick = (clip: AiHighlightClip) => {
    soundSynth.playWinFanfare();
    onPlayClip(clip);
  };

  const clipGradients = [
    'from-blue-900/60 via-slate-900 to-black',
    'from-rose-900/60 via-slate-900 to-black',
    'from-amber-900/60 via-slate-900 to-black'
  ];

  return (
    <div className="glass-panel p-4 border border-white/10 shadow-xl">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30">
            <Film className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-display font-bold text-white">
              AI REAL-TIME HIGHLIGHT CLIPS
            </h4>
            <p className="text-[10px] text-slate-400 font-mono">
              VLM Automated Dead-Time Extraction
            </p>
          </div>
        </div>

        <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30 font-mono font-bold">
          {highlights.length} Clips Ready
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        {highlights.map((clip, idx) => (
          <div
            key={clip.clipId}
            onClick={() => handleClipClick(clip)}
            className="group p-2.5 rounded-xl bg-black/40 border border-white/10 hover:border-cyan-400/50 hover:bg-white/5 transition-all cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className={`relative rounded-lg overflow-hidden mb-2 aspect-video bg-gradient-to-br ${clipGradients[idx % 3]} flex items-center justify-center border border-white/5`}>
                <div className="absolute inset-0 bg-[radial-gradient(#00f0ff_1px,transparent_1px)] [background-size:12px_12px] opacity-20" />
                <div className="w-9 h-9 rounded-full bg-cyan-400 text-black flex items-center justify-center shadow-[0_0_15px_#00f0ff] group-hover:scale-110 transition-transform">
                  <Play className="w-4 h-4 fill-black ml-0.5" />
                </div>

                <div className="absolute top-1.5 right-1.5 px-2 py-0.5 rounded bg-black/80 text-[10px] font-mono text-amber-300 border border-white/10 flex items-center gap-1">
                  <Volume2 className="w-3 h-3 text-rose-400" />
                  <span>{clip.crowdDecibelPeak} dB</span>
                </div>
              </div>

              <h5 className="text-xs font-display font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-1">
                {clip.title}
              </h5>
              <p className="text-[10px] text-slate-400 font-sans line-clamp-2 mt-1">
                {clip.aiExplanation}
              </p>
            </div>

            <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-white/10">
              {clip.tags.slice(0, 3).map((t) => (
                <span
                  key={t}
                  className="text-[9px] px-1.5 py-0.2 rounded bg-white/5 text-slate-300 font-mono"
                >
                  #{t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
