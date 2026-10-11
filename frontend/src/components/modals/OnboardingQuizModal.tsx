import React, { useState } from 'react';
import { Sparkles, Check, ArrowRight, Brain, Zap, Activity, Shield } from 'lucide-react';
import { PersonaType } from '../../types';
import { soundSynth } from '../../services/audioSynth';
import confetti from 'canvas-confetti';

interface OnboardingQuizModalProps {
  onComplete: (persona: PersonaType) => void;
  onClose: () => void;
}

export const OnboardingQuizModal: React.FC<OnboardingQuizModalProps> = ({
  onComplete,
  onClose
}) => {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);

  const questions = [
    {
      title: 'How do you prefer to experience live sports?',
      options: [
        { label: '🔥 Fast-paced micro-bets, memes, and live streaks', persona: 'GEN_Z' as PersonaType },
        { label: '🧠 Relaxed viewing with simple, plain-English rule explanations', persona: 'CASUAL' as PersonaType },
        { label: '📊 Deep telemetry, tactical radar, and historical statistics', persona: 'HARDCORE' as PersonaType },
        { label: '🛡️ Cheering in watch parties with my fan club / clan', persona: 'CLUB_MEMBER' as PersonaType }
      ]
    },
    {
      title: 'When a referee or umpire makes a controversial call, you want:',
      options: [
        { label: 'A 15-second instant prediction on the verdict with $SYNC tokens', persona: 'GEN_Z' as PersonaType },
        { label: 'A 1-sentence plain English summary of why the call was made', persona: 'CASUAL' as PersonaType },
        { label: 'Ball trajectory, contact angle, and historical conversion metrics', persona: 'HARDCORE' as PersonaType },
        { label: 'To rally my clan in the chat and coordinate our group vote', persona: 'CLUB_MEMBER' as PersonaType }
      ]
    },
    {
      title: 'What camera angle do you care most about?',
      options: [
        { label: 'Player Head-Cam / Athlete POV for high-intensity action', persona: 'GEN_Z' as PersonaType },
        { label: 'Standard 4K Broadcast TV feed with clear scorebugs', persona: 'CASUAL' as PersonaType },
        { label: '2D Sky Tactical Pitch Radar to analyze pressing formations', persona: 'HARDCORE' as PersonaType },
        { label: '360° Stadium Endzone Fan view to feel the stadium roar', persona: 'CLUB_MEMBER' as PersonaType }
      ]
    }
  ];

  const handleSelectOption = (persona: PersonaType) => {
    soundSynth.playCoinChime();
    const nextAnswers = [...answers, persona];
    setAnswers(nextAnswers);

    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      // Determine dominant persona
      const counts: Record<string, number> = {};
      nextAnswers.forEach((p) => { counts[p] = (counts[p] || 0) + 1; });
      let dominant: PersonaType = 'GEN_Z';
      let maxCount = 0;
      for (const p in counts) {
        if (counts[p] > maxCount) {
          maxCount = counts[p];
          dominant = p as PersonaType;
        }
      }

      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#00f0ff', '#ff0055', '#9d4edd', '#ffd700']
      });

      onComplete(dominant);
    }
  };

  const currentQ = questions[step];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-lg cosmic-glass-thick p-6 border border-cyan-500/50 shadow-[0_0_50px_rgba(0,240,255,0.3)] relative">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              <Sparkles className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <h3 className="text-base font-bold font-display text-white">
                AI PERSONA CALIBRATION QUIZ
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Step {step + 1} of {questions.length} • Multi-Audience Engine
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

        {/* Progress Bar */}
        <div className="w-full h-1.5 rounded-full bg-slate-800 mb-4 overflow-hidden">
          <div
            className="h-full bg-cyan-400 transition-all duration-300 shadow-[0_0_8px_#00f0ff]"
            style={{ width: `${((step + 1) / questions.length) * 100}%` }}
          />
        </div>

        {/* Question Title */}
        <h4 className="text-sm sm:text-base font-bold text-white font-heading mb-4 leading-relaxed">
          {currentQ.title}
        </h4>

        {/* Options */}
        <div className="space-y-2.5">
          {currentQ.options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectOption(opt.persona)}
              className="w-full p-3.5 rounded-xl bg-slate-900/70 hover:bg-cyan-950/40 border border-white/10 hover:border-cyan-500/50 text-left text-xs sm:text-sm font-medium text-slate-200 hover:text-white transition-all flex items-center justify-between group"
            >
              <span>{opt.label}</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
            </button>
          ))}
        </div>

      </div>
    </div>
  );
};
