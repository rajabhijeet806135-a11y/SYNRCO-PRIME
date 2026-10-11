import { 
  MatchInfo, 
  MatchTelemetry, 
  ContextualPrediction, 
  CrowdDecibelSnapshot, 
  ClanInfo, 
  ClanChatMessage, 
  LeaderboardUser, 
  UserProfile,
  SponsoredMoment,
  AiHighlightClip
} from '../types';

const API_BASE = '/api/v1';

// Seed Mock Data for Resilient Offline / Demo Mode
export const INITIAL_MATCHES: MatchInfo[] = [
  {
    id: 'IND_AUS_T20_2026',
    sport: 'CRICKET',
    title: 'T20 World Cup Super 8s',
    homeTeam: 'India',
    awayTeam: 'Australia',
    homeScore: '184/3 (17.4 ov)',
    awayScore: '182/7 (20.0 ov)',
    status: 'LIVE',
    gameClock: 'Over 17.4',
    venue: 'Kensington Oval, Barbados',
    winProbabilityHome: 86,
    momentumTeam: 'home',
    metadata: {
      requiredRuns: 0,
      ballsRemaining: 14,
      crr: '10.41',
      rrr: '0.00',
      batsmanStriker: 'V. Kohli 78* (44)',
      batsmanNonStriker: 'H. Pandya 24* (11)',
      bowler: 'M. Starc 1/34 (3.4 ov)'
    }
  },
  {
    id: 'MCI_RMA_UCL_2026',
    sport: 'FOOTBALL',
    title: 'UEFA Champions League Quarter-Final',
    homeTeam: 'Manchester City',
    awayTeam: 'Real Madrid',
    homeScore: '2',
    awayScore: '2',
    status: 'LIVE',
    gameClock: '88:42',
    venue: 'Etihad Stadium, Manchester',
    winProbabilityHome: 52,
    momentumTeam: 'away',
    metadata: {
      xGHome: 2.14,
      xGAway: 1.88,
      possessionHome: 64,
      shotsOnTargetHome: 8,
      shotsOnTargetAway: 6,
      lastEvent: 'VAR Check Penalty in Progress'
    }
  },
  {
    id: 'LAL_GSW_NBA_2026',
    sport: 'BASKETBALL',
    title: 'NBA Western Conference Clash',
    homeTeam: 'LA Lakers',
    awayTeam: 'Golden State Warriors',
    homeScore: '108',
    awayScore: '109',
    status: 'LIVE',
    gameClock: 'Q4 0:24',
    venue: 'Crypto.com Arena, Los Angeles',
    winProbabilityHome: 46,
    momentumTeam: 'home',
    metadata: {
      shotClock: '14s',
      timeoutsHome: 1,
      timeoutsAway: 0,
      leadChanges: 18,
      topScorer: 'L. James 34 PTS, 9 AST'
    }
  }
];

export const INITIAL_USER: UserProfile = {
  userId: 'usr_cosmic_99',
  username: 'AstroStriker',
  email: 'fan@syncroprime.io',
  persona: 'GEN_Z',
  syncTokens: 1450,
  xp: 4280,
  level: 14,
  currentStreak: 3,
  highestStreak: 7,
  tier: 'Gold',
  clanId: 'clan_mumbai_army',
  sybilTrustScore: 0.96
};

export const INITIAL_CLANS: ClanInfo[] = [
  { id: 'clan_mumbai_army', name: 'Cosmic Paltan 🚀', sport: 'CRICKET', badge: '🛡️', memberCount: 4120, totalXp: 984500, rank: 1 },
  { id: 'clan_cityzens', name: 'Blue Moon Space Clan 🌙', sport: 'FOOTBALL', badge: '⚡', memberCount: 3890, totalXp: 871200, rank: 2 },
  { id: 'clan_madridistas', name: 'Galácticos Orbit 👑', sport: 'FOOTBALL', badge: '🪐', memberCount: 3640, totalXp: 815000, rank: 3 },
  { id: 'clan_lakers_nation', name: 'Purple & Gold Nebula 🌟', sport: 'BASKETBALL', badge: '🏆', memberCount: 2950, totalXp: 692000, rank: 4 }
];

export const INITIAL_LEADERBOARD: LeaderboardUser[] = [
  { rank: 1, userId: 'u_1', username: 'HyperNova', avatar: '⚡', score: 18400, streak: 8, persona: 'GEN_Z', tier: 'Diamond', clanId: 'clan_mumbai_army' },
  { rank: 2, userId: 'u_2', username: 'TacticalOrion', avatar: '🪐', score: 16950, streak: 5, persona: 'HARDCORE', tier: 'Diamond', clanId: 'clan_cityzens' },
  { rank: 3, userId: 'u_3', username: 'AstroStriker', avatar: '🚀', score: 14280, streak: 3, persona: 'GEN_Z', tier: 'Gold', clanId: 'clan_mumbai_army' },
  { rank: 4, userId: 'u_4', username: 'VortexFan', avatar: '🌌', score: 12100, streak: 4, persona: 'CLUB_MEMBER', tier: 'Gold', clanId: 'clan_madridistas' },
  { rank: 5, userId: 'u_5', username: 'EchoClutch', avatar: '☄️', score: 10450, streak: 2, persona: 'CASUAL', tier: 'Silver', clanId: 'clan_lakers_nation' },
];

export const INITIAL_SPONSORS: SponsoredMoment[] = [
  {
    campaignKey: 'nike_speed_cricket',
    sponsorName: 'Nike Pro Fuel',
    sponsorLogo: '⚡ NIKE',
    tagline: 'Just Do It at Light Speed',
    challengeTitle: 'Nike 145km/h Speed Challenge: Will this delivery cross 145 km/h?',
    rewardBonusXp: 250,
    rewardSyncTokens: 100
  },
  {
    campaignKey: 'rolex_clutch_time',
    sponsorName: 'Rolex Chrono',
    sponsorLogo: '👑 ROLEX',
    tagline: 'Perpetual Excellence in Stoppage Time',
    challengeTitle: 'Rolex 90th Min Clutch Goal Prediction',
    rewardBonusXp: 500,
    rewardSyncTokens: 250
  },
  {
    campaignKey: 'puma_nitro_dunk',
    sponsorName: 'Puma Nitro',
    sponsorLogo: '🐆 PUMA',
    tagline: 'Forever Faster',
    challengeTitle: 'Puma Above the Rim: Clutch 3-pointer buzzer beater?',
    rewardBonusXp: 300,
    rewardSyncTokens: 150
  }
];

export const INITIAL_HIGHLIGHTS: AiHighlightClip[] = [
  {
    clipId: 'ind_aus_6s',
    matchId: 'IND_AUS_T20_2026',
    title: 'Kohli 98m Cosmic Six over Long-On',
    timestampSec: 1042,
    thumbnailUrl: 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=600&q=80',
    aiExplanation: 'Ball struck at 148 km/h exit velocity, 32° launch angle. Perfect wrist snapshot over deep boundary.',
    crowdDecibelPeak: 114.8,
    tags: ['SIX', 'CLUTCH', 'KOHLI', '148 KM/H']
  },
  {
    clipId: 'mci_rma_var',
    matchId: 'MCI_RMA_UCL_2026',
    title: 'De Bruyne Cross & VAR Handball Review',
    timestampSec: 5320,
    thumbnailUrl: 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80',
    aiExplanation: 'Referee called to pitchside monitor. Ball trajectory indicates contact with arm outside natural silhouette.',
    crowdDecibelPeak: 109.2,
    tags: ['VAR', 'PENALTY', 'UCL', 'DRAMA']
  },
  {
    clipId: 'lal_gsw_clutch',
    matchId: 'LAL_GSW_NBA_2026',
    title: 'Curry 32-Foot Deep Stepback',
    timestampSec: 2840,
    thumbnailUrl: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=600&q=80',
    aiExplanation: 'Stepback separation of 1.4 meters created against contest. Shot release apex 4.1 meters.',
    crowdDecibelPeak: 112.5,
    tags: ['STEPBACK', 'CURRY', 'DEEP 3', 'NBA']
  }
];

export class ApiService {
  // Matches
  static async getMatches(): Promise<MatchInfo[]> {
    try {
      const res = await fetch(`${API_BASE}/matches`);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend unavailable, using simulated match data');
    }
    return INITIAL_MATCHES;
  }

  // Active Predictions
  static async getPredictions(matchId: string): Promise<ContextualPrediction[]> {
    try {
      const res = await fetch(`${API_BASE}/predictions/active/${matchId}`);
      if (res.ok) return await res.json();
    } catch (e) {
      // fallback
    }
    return [];
  }

  // Submit Vote
  static async submitVote(
    matchId: string, 
    predictionId: string, 
    selectedOption: string, 
    stake: number,
    reactionSpeedMs: number = 2200
  ) {
    try {
      const res = await fetch(`${API_BASE}/predictions/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prediction_id: predictionId,
          selected_option: selectedOption,
          stake_tokens: stake,
          client_event_id: `vote_${Date.now()}`,
          reaction_speed_ms: reactionSpeedMs
        })
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Offline vote fallback simulated');
    }
    return { accepted: true, stake, balance: 1400, oddsMultiplier: 2.1 };
  }

  // Cheer / Decibel Record
  static async recordCheer(matchId: string, intensity: number = 1.0): Promise<CrowdDecibelSnapshot> {
    try {
      const res = await fetch(`${API_BASE}/matches/${matchId}/cheer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intensity })
      });
      if (res.ok) return await res.json();
    } catch (e) {
      // fallback
    }
    return {
      matchId,
      currentDecibels: Math.min(120, Math.round(92 + Math.random() * 20 * intensity)),
      peakDecibels: 118.4,
      cheerCountTotal: 48201 + Math.floor(Math.random() * 50),
      hypeLevel: intensity > 1.5 ? 'ROARING' : 'HYPED',
      vibeHapticThreshold: true
    };
  }

  // Leaderboards
  static async getLeaderboard(matchId: string): Promise<LeaderboardUser[]> {
    try {
      const res = await fetch(`${API_BASE}/leaderboards/global/${matchId}`);
      if (res.ok) return await res.json();
    } catch (e) {}
    return INITIAL_LEADERBOARD;
  }

  // Clans
  static async getClans(): Promise<ClanInfo[]> {
    try {
      const res = await fetch(`${API_BASE}/clans`);
      if (res.ok) return await res.json();
    } catch (e) {}
    return INITIAL_CLANS;
  }

  // Highlights
  static async getHighlights(matchId: string): Promise<AiHighlightClip[]> {
    try {
      const res = await fetch(`${API_BASE}/matches/${matchId}/highlights`);
      if (res.ok) return await res.json();
    } catch (e) {}
    return INITIAL_HIGHLIGHTS;
  }

  // Sponsors
  static async getSponsors(): Promise<SponsoredMoment[]> {
    try {
      const res = await fetch(`${API_BASE}/broadcaster/sponsors`);
      if (res.ok) return await res.json();
    } catch (e) {}
    return INITIAL_SPONSORS;
  }
}
