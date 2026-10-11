import React, { useState, useEffect } from 'react';
import { 
  MatchInfo, 
  SportType, 
  PersonaType, 
  CameraAngle, 
  MatchTelemetry, 
  ContextualPrediction, 
  CrowdDecibelSnapshot, 
  UserProfile,
  ClanInfo,
  LeaderboardUser,
  SponsoredMoment,
  AiHighlightClip
} from './types';

// Services
import { ApiService, INITIAL_MATCHES, INITIAL_USER, INITIAL_CLANS, INITIAL_LEADERBOARD, INITIAL_SPONSORS, INITIAL_HIGHLIGHTS } from './services/api';
import { wsClient } from './services/websocket';
import { soundSynth } from './services/audioSynth';
import confetti from 'canvas-confetti';

// Components
import { CosmicStarfield } from './components/common/CosmicStarfield';
import { TopNavigation } from './components/header/TopNavigation';
import { PersonaSelector } from './components/header/PersonaSelector';
import { MatchHeroStream } from './components/match/MatchHeroStream';
import { LiveScoreboard } from './components/match/LiveScoreboard';
import { DecibelResonator } from './components/match/DecibelResonator';

// Personas Hubs
import { GenZInteractiveHub } from './components/personas/GenZInteractiveHub';
import { CasualExplainerHub } from './components/personas/CasualExplainerHub';
import { HardcoreAnalyticsHub } from './components/personas/HardcoreAnalyticsHub';
import { ClanLoungeHub } from './components/personas/ClanLoungeHub';
import { StadiumExperienceHub } from './components/personas/StadiumExperienceHub';
import { BroadcasterHub } from './components/personas/BroadcasterHub';

// Gamification
import { LeaderboardPanel } from './components/gamification/LeaderboardPanel';
import { FanRewardsVault } from './components/gamification/FanRewardsVault';
import { AiHighlightsDrawer } from './components/gamification/AiHighlightsDrawer';

// Modals
import { OnboardingQuizModal } from './components/modals/OnboardingQuizModal';
import { HistoricalH2HModal } from './components/modals/HistoricalH2HModal';

export const App: React.FC = () => {
  // State
  const [matches, setMatches] = useState<MatchInfo[]>(INITIAL_MATCHES);
  const [selectedMatch, setSelectedMatch] = useState<MatchInfo>(INITIAL_MATCHES[0]);
  const [selectedSport, setSelectedSport] = useState<SportType | 'ALL'>('ALL');
  const [currentPersona, setCurrentPersona] = useState<PersonaType>('GEN_Z');
  const [activeCamera, setActiveCamera] = useState<CameraAngle>('MAIN_BROADCAST');
  
  // Real-Time Telemetry & Data
  const [telemetry, setTelemetry] = useState<MatchTelemetry | null>(null);
  const [crowdSnapshot, setCrowdSnapshot] = useState<CrowdDecibelSnapshot | null>(null);
  const [activePrediction, setActivePrediction] = useState<ContextualPrediction | null>(null);
  const [activeStoppage, setActiveStoppage] = useState<string | null>('DRS Ball Tracking Appeal (Starc to Kohli)');
  const [isOnline, setIsOnline] = useState<boolean>(true);

  // User State
  const [user, setUser] = useState<UserProfile>(INITIAL_USER);
  const [clans, setClans] = useState<ClanInfo[]>(INITIAL_CLANS);
  const [leaderboard, setLeaderboard] = useState<LeaderboardUser[]>(INITIAL_LEADERBOARD);
  const [sponsors, setSponsors] = useState<SponsoredMoment[]>(INITIAL_SPONSORS);
  const [highlights, setHighlights] = useState<AiHighlightClip[]>(INITIAL_HIGHLIGHTS);

  // Modals
  const [isQuizOpen, setIsQuizOpen] = useState(false);
  const [isHistoricalOpen, setIsHistoricalOpen] = useState(false);
  const [isVaultOpen, setIsVaultOpen] = useState(false);
  const [activeClipModal, setActiveClipModal] = useState<AiHighlightClip | null>(null);

  // Filtered Matches
  const filteredMatches = selectedSport === 'ALL'
    ? matches
    : matches.filter(m => m.sport === selectedSport);

  // Listen to WebSocket Events
  useEffect(() => {
    const unsubTelemetry = wsClient.on('TELEMETRY_UPDATE', (data: MatchTelemetry) => {
      setTelemetry(data);
    });

    const unsubCrowd = wsClient.on('CROWD_DECIBELS', (data: CrowdDecibelSnapshot) => {
      setCrowdSnapshot(data);
    });

    const unsubPredictions = wsClient.on('CONTEXTUAL_EVENT', (data: any) => {
      setActiveStoppage(data.event_type || 'Match Stoppage Review');
    });

    const unsubStatus = wsClient.on('CONNECTION_STATUS', ({ connected }) => {
      setIsOnline(connected);
    });

    return () => {
      unsubTelemetry();
      unsubCrowd();
      unsubPredictions();
      unsubStatus();
    };
  }, []);

  // Handle Match Selection
  const handleSelectMatch = (match: MatchInfo) => {
    setSelectedMatch(match);
    wsClient.subscribeMatch(match.id);
    setActiveStoppage(
      match.sport === 'CRICKET'
        ? 'DRS Ball Tracking Review: Starc to Kohli'
        : match.sport === 'FOOTBALL'
        ? 'VAR Handball & Penalty Deliberation'
        : 'Clutch 4th Quarter Free Throw Review'
    );
  };

  // Handle Vote Submission
  const handleVote = (predictionId: string, option: string, stake: number) => {
    wsClient.sendVote(selectedMatch.id, predictionId, option, stake);
    
    // Optimistic balance & XP update
    setUser(prev => ({
      ...prev,
      syncTokens: prev.syncTokens + Math.round(stake * 1.5),
      xp: prev.xp + 150,
      currentStreak: prev.currentStreak + 1
    }));
  };

  // Handle Persona Quiz Completion
  const handleQuizComplete = (newPersona: PersonaType) => {
    setCurrentPersona(newPersona);
    setUser(prev => ({ ...prev, persona: newPersona }));
    setIsQuizOpen(false);
    soundSynth.playWinFanfare();
  };

  // Handle Perk Redemption
  const handleRedeemPerk = (cost: number) => {
    setUser(prev => ({
      ...prev,
      syncTokens: Math.max(0, prev.syncTokens - cost)
    }));
  };

  // Handle Sponsor Trigger
  const handleTriggerSponsor = (sp: SponsoredMoment) => {
    soundSynth.playAlertSound();
    setActiveStoppage(`Sponsored Moment: ${sp.challengeTitle}`);
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.7 },
      colors: ['#ffd700', '#00f0ff', '#ff0055']
    });
  };

  return (
    <div className="relative min-h-screen text-slate-100 bg-[#06070d] font-sans selection:bg-cyan-500 selection:text-black">
      
      {/* 3D Cosmic Starfield Canvas */}
      <CosmicStarfield />

      {/* Main Orchestration */}
      <div className="relative z-10 flex flex-col min-h-screen">
        
        {/* Top Space Command Navigation Bar */}
        <TopNavigation
          matches={filteredMatches}
          selectedMatch={selectedMatch}
          onSelectMatch={handleSelectMatch}
          selectedSport={selectedSport}
          onSelectSport={setSelectedSport}
          user={user}
          onOpenQuiz={() => setIsQuizOpen(true)}
          onOpenHistorical={() => setIsHistoricalOpen(true)}
          onOpenVault={() => setIsVaultOpen(true)}
          isOnline={isOnline}
        />

        {/* Command Center Split Grid */}
        <main className="flex-1 max-w-[1600px] w-full mx-auto p-3 sm:p-5">
          
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start mb-4">
            
            {/* Left 7/8 Cols: Live Broadcast Player, Scoreboard & Commentary */}
            <div className="md:col-span-7 xl:col-span-8 space-y-3.5">
              
              {/* Broadcast Stream Player */}
              <MatchHeroStream
                match={selectedMatch}
                telemetry={telemetry}
                currentPersona={currentPersona}
                activeStoppage={activeStoppage}
                onSelectCamera={setActiveCamera}
                activeCamera={activeCamera}
              />

              {/* Live Match Scorebug */}
              <LiveScoreboard match={selectedMatch} />

              {/* Live Match Event & Commentary Ticker */}
              <div className="glass-panel p-3 border border-white/10 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span className="text-cyan-300 font-bold">17.4 ov:</span>
                  <span className="text-slate-200">
                    Starc bowls 144.2 km/h full delivery • Kohli drives through covers for FOUR!
                  </span>
                </div>
                <span className="text-[10px] text-amber-400 hidden sm:inline font-bold">
                  Exit: 148 km/h • xBoundary: 0.88
                </span>
              </div>

            </div>

            {/* Right 5/4 Cols: Interactive Cockpit, Persona Hub, Decibels & Leaderboard */}
            <div className="md:col-span-5 xl:col-span-4 space-y-3">
              
              {/* Persona Cockpit Mode Selector */}
              <PersonaSelector
                currentPersona={currentPersona}
                onSelectPersona={setCurrentPersona}
              />

              {/* Dynamic Persona Experience Panel */}
              {currentPersona === 'GEN_Z' && (
                <GenZInteractiveHub
                  match={selectedMatch}
                  user={user}
                  onVote={handleVote}
                  activePrediction={activePrediction}
                />
              )}

              {currentPersona === 'CASUAL' && (
                <CasualExplainerHub match={selectedMatch} />
              )}

              {currentPersona === 'HARDCORE' && (
                <HardcoreAnalyticsHub
                  match={selectedMatch}
                  telemetry={telemetry}
                  onOpenHistorical={() => setIsHistoricalOpen(true)}
                />
              )}

              {currentPersona === 'CLUB_MEMBER' && (
                <ClanLoungeHub
                  match={selectedMatch}
                  user={user}
                  clans={clans}
                />
              )}

              {currentPersona === 'STADIUM' && (
                <StadiumExperienceHub
                  match={selectedMatch}
                  isOnline={isOnline}
                />
              )}

              {currentPersona === 'BROADCASTER' && (
                <BroadcasterHub
                  match={selectedMatch}
                  sponsors={sponsors}
                  onTriggerSponsor={handleTriggerSponsor}
                />
              )}

              {/* Stadium Crowd Decibel Resonator */}
              <DecibelResonator
                matchId={selectedMatch.id}
                crowdSnapshot={crowdSnapshot}
              />

              {/* CQRS Global & Clan Leaderboards */}
              <LeaderboardPanel
                users={leaderboard}
                clans={clans}
                currentUser={user}
              />

            </div>

          </div>

          {/* AI Highlight Clips Drawer - Full Width Across Bottom */}
          <AiHighlightsDrawer
            highlights={highlights}
            onPlayClip={(clip) => setActiveClipModal(clip)}
          />

        </main>

        {/* Sleek Footer */}
        <footer className="w-full border-t border-white/5 py-3 px-6 text-center text-xs text-slate-500 font-mono">
          <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>SYNCRO PRIME v2.4 • Real-Time AI Fan Companion Engine</span>
            <div className="flex items-center gap-3">
              <span className="text-cyan-400">CQRS &lt;18ms</span>
              <span>•</span>
              <span className="text-purple-400">6 Personas Active</span>
              <span>•</span>
              <span className="text-amber-400">100% Sybil Protected</span>
            </div>
          </div>
        </footer>

      </div>

      {/* Modals */}
      {isQuizOpen && (
        <OnboardingQuizModal
          onComplete={handleQuizComplete}
          onClose={() => setIsQuizOpen(false)}
        />
      )}

      {isHistoricalOpen && (
        <HistoricalH2HModal
          onClose={() => setIsHistoricalOpen(false)}
        />
      )}

      {isVaultOpen && (
        <FanRewardsVault
          user={user}
          onRedeemPerk={handleRedeemPerk}
          onClose={() => setIsVaultOpen(false)}
        />
      )}

      {/* Highlight Replay Modal */}
      {activeClipModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-lg glass-panel p-5 border border-cyan-500/50 shadow-2xl relative">
            <div className="flex items-center justify-between mb-3 border-b border-white/10 pb-2">
              <h3 className="text-sm font-display font-bold text-white">{activeClipModal.title}</h3>
              <button
                onClick={() => setActiveClipModal(null)}
                className="w-7 h-7 rounded-lg bg-white/10 text-white flex items-center justify-center text-xs font-mono font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>
            <div className="relative aspect-video rounded-xl overflow-hidden bg-black mb-3 border border-white/10 flex items-center justify-center">
              <div className="px-4 py-2 rounded-xl bg-rose-600/90 text-white font-mono text-xs font-bold animate-pulse">
                REPLAYING 4K VLM CLIP (PEAK: {activeClipModal.crowdDecibelPeak} dB)
              </div>
            </div>
            <p className="text-xs text-slate-300">{activeClipModal.aiExplanation}</p>
          </div>
        </div>
      )}

    </div>
  );
};

export default App;
