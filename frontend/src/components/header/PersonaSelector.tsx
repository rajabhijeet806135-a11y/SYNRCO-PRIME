import React from 'react';
import { Zap, Brain, Activity, Shield, MapPin, Radio } from 'lucide-react';
import { PersonaType } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface PersonaSelectorProps {
  currentPersona: PersonaType;
  onSelectPersona: (persona: PersonaType) => void;
}

interface PersonaTab {
  id: PersonaType;
  label: string;
  icon: React.ReactNode;
  activeColor: string;
  glowShadow: string;
}

export const PersonaSelector: React.FC<PersonaSelectorProps> = ({
  currentPersona,
  onSelectPersona
}) => {
  const tabs: PersonaTab[] = [
    {
      id: 'GEN_Z',
      label: 'Gen-Z Hype',
      icon: <Zap className="w-3.5 h-3.5" />,
      activeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/80',
      glowShadow: 'shadow-[0_0_15px_rgba(255,0,85,0.4)]'
    },
    {
      id: 'CASUAL',
      label: 'Casual AI Guide',
      icon: <Brain className="w-3.5 h-3.5" />,
      activeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-400/80',
      glowShadow: 'shadow-[0_0_15px_rgba(0,240,255,0.4)]'
    },
    {
      id: 'HARDCORE',
      label: 'Pro Telemetry',
      icon: <Activity className="w-3.5 h-3.5" />,
      activeColor: 'bg-purple-500/20 text-purple-300 border-purple-500/80',
      glowShadow: 'shadow-[0_0_15px_rgba(157,78,221,0.4)]'
    },
    {
      id: 'CLUB_MEMBER',
      label: 'Clan War',
      icon: <Shield className="w-3.5 h-3.5" />,
      activeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/80',
      glowShadow: 'shadow-[0_0_15px_rgba(255,183,3,0.4)]'
    },
    {
      id: 'STADIUM',
      label: 'Stadium AR',
      icon: <MapPin className="w-3.5 h-3.5" />,
      activeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-400/80',
      glowShadow: 'shadow-[0_0_15px_rgba(0,255,136,0.4)]'
    },
    {
      id: 'BROADCASTER',
      label: 'Broadcaster SDK',
      icon: <Radio className="w-3.5 h-3.5" />,
      activeColor: 'bg-blue-500/20 text-blue-300 border-blue-400/80',
      glowShadow: 'shadow-[0_0_15px_rgba(58,134,255,0.4)]'
    }
  ];

  const handleSelect = (p: PersonaType) => {
    soundSynth.playAlertSound();
    onSelectPersona(p);
  };

  return (
    <div className="w-full glass-panel p-1.5 flex flex-wrap items-center justify-between gap-2 border border-white/10 shadow-lg">
      <div className="flex items-center gap-2 pl-2">
        <span className="text-[10px] font-brand tracking-widest text-slate-400 uppercase">
          COCKPIT MODE:
        </span>
        <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono font-bold">
          {currentPersona}
        </span>
      </div>

      <div className="flex items-center gap-1.5 overflow-x-auto max-w-full py-0.5">
        {tabs.map((tab) => {
          const isActive = currentPersona === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => handleSelect(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-display font-bold border transition-all whitespace-nowrap ${
                isActive
                  ? `${tab.activeColor} ${tab.glowShadow} scale-[1.02]`
                  : 'bg-white/5 border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/10'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
