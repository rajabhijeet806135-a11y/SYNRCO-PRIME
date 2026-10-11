import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { soundSynth } from '../../services/audioSynth';

export const SoundToggle: React.FC = () => {
  const [muted, setMuted] = useState(soundSynth.getIsMuted());

  const toggleSound = () => {
    const next = !muted;
    setMuted(next);
    soundSynth.setMuted(next);
    if (!next) {
      soundSynth.playCoinChime();
    }
  };

  return (
    <button
      onClick={toggleSound}
      title={muted ? 'Unmute Stadium Audio FX' : 'Mute Audio FX'}
      className="flex items-center justify-center w-9 h-9 rounded-xl cosmic-glass border border-white/10 hover:border-cyan-500/40 text-slate-300 hover:text-cyan-400 transition-all shadow-[0_0_12px_rgba(0,0,0,0.4)]"
    >
      {muted ? <VolumeX className="w-4 h-4 text-slate-500" /> : <Volume2 className="w-4 h-4 text-cyan-400 animate-pulse" />}
    </button>
  );
};
