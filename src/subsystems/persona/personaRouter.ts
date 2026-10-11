import { PersonaType } from '../../config/index.js';
import { ContextualEventData } from '../../datasets/dataset2_events.js';
import { MultiSportTelemetryData } from '../../datasets/dataset1_telemetry.js';

export interface PersonaAdaptedPayload {
  persona: PersonaType;
  matchId: string;
  uiMode: string;
  title: string;
  content: {
    headline: string;
    subtext: string;
    actionType: 'POLL' | 'PREDICTION' | 'TELEMETRY_CARD' | 'CLAN_BATTLE' | 'STADIUM_AR' | 'BROADCAST_OVERLAY';
    actionPayload: any;
    gamificationHint?: string;
  };
  metrics?: {
    xg?: number;
    ballSpeed?: number;
    strikeRate?: number;
    decibels?: number;
  };
}

export class PersonaRouter {
  /**
   * Adapts a contextual match event into a persona-specific experience
   */
  public static adaptContextualEvent(event: ContextualEventData, persona: PersonaType): PersonaAdaptedPayload {
    switch (persona) {
      case 'CASUAL':
        return {
          persona: 'CASUAL',
          matchId: event.match_id,
          uiMode: 'SIMPLIFIED_EXPLANATION',
          title: 'Easy AI Match Explainer',
          content: {
            headline: event.prompts_generated.casual,
            subtext: event.contextual_narrative,
            actionType: 'POLL',
            actionPayload: {
              question: event.prompts_generated.casual,
              options: ['Yes', 'No'],
            },
            gamificationHint: 'Earn +25 Fan XP for voting!',
          },
        };

      case 'GEN_Z':
        return {
          persona: 'GEN_Z',
          matchId: event.match_id,
          uiMode: 'RAPID_MICRO_PREDICTION',
          title: '15s Rapid Micro-Challenge 🔥',
          content: {
            headline: event.prompts_generated.genz,
            subtext: `Window closes in ${event.estimated_dead_time_seconds}s!`,
            actionType: 'PREDICTION',
            actionPayload: {
              predictionId: `pred_${event.event_id}`,
              question: event.prompts_generated.genz,
              options: event.prediction_options || ['Option A', 'Option B'],
              odds: event.odds || { 'Option A': 2.0, 'Option B': 2.0 },
              windowSeconds: event.estimated_dead_time_seconds,
            },
            gamificationHint: 'Active 2.5x Streak Multiplier Enabled ⚡',
          },
        };

      case 'HARDCORE':
        return {
          persona: 'HARDCORE',
          matchId: event.match_id,
          uiMode: 'TACTICAL_DEEP_DIVE',
          title: 'Advanced Telemetry & Predictive Analytics',
          content: {
            headline: event.prompts_generated.hardcore,
            subtext: `Event Type: ${event.event_type} | AI Confidence: 94.2%`,
            actionType: 'TELEMETRY_CARD',
            actionPayload: {
              predictionId: `pred_${event.event_id}`,
              question: event.prompts_generated.hardcore,
              options: event.prediction_options,
              odds: event.odds,
            },
          },
        };

      case 'CLUB_MEMBER':
        return {
          persona: 'CLUB_MEMBER',
          matchId: event.match_id,
          uiMode: 'CLAN_WAR_CLASH',
          title: 'Clan Battle Arena ⚔️',
          content: {
            headline: event.prompts_generated.club_member || 'Clan Battle Alert!',
            subtext: 'Every member vote contributes to your Clan Leaderboard rank!',
            actionType: 'CLAN_BATTLE',
            actionPayload: {
              predictionId: `pred_${event.event_id}`,
              options: event.prediction_options,
            },
            gamificationHint: '+100 Clan War Glory Points on win',
          },
        };

      case 'STADIUM':
        return {
          persona: 'STADIUM',
          matchId: event.match_id,
          uiMode: 'IN_STADIUM_5G_EXPERIENCE',
          title: 'In-Stadium 5G Live View',
          content: {
            headline: event.prompts_generated.stadium || 'Live Stadium Replay Available',
            subtext: 'Synchronized with stadium audio system',
            actionType: 'STADIUM_AR',
            actionPayload: {
              seatViewAngle: 'CAMERA_POV_ENDZONE',
              stadiumDeliveryAvailable: true,
            },
          },
        };

      case 'BROADCASTER':
        return {
          persona: 'BROADCASTER',
          matchId: event.match_id,
          uiMode: 'BROADCAST_SDK_OVERLAY',
          title: 'Broadcaster Interactive Real Estate',
          content: {
            headline: event.prompts_generated.broadcaster || 'Official Matchday Poll',
            subtext: 'Embeddable SDK layer for OTT stream',
            actionType: 'BROADCAST_OVERLAY',
            actionPayload: {
              sponsorBrand: 'HawkEye & Nike',
              interactiveCta: 'Vote Now on Stream',
            },
          },
        };
    }
  }

  /**
   * Adapts raw optical telemetry for persona visual consumption
   */
  public static adaptTelemetry(telemetry: MultiSportTelemetryData, persona: PersonaType): any {
    if (persona === 'HARDCORE') {
      return telemetry; // Full raw coordinates, xG, Hawkeye vectors, heart rates
    }

    if (persona === 'GEN_Z') {
      return {
        matchId: telemetry.match_id,
        sport: telemetry.sport,
        ballSpeedKmh: telemetry.ball.speed_kmh,
        hypeFactor: telemetry.ball.speed_kmh > 120 ? 'HIGH_SPEED_ROCKET 🚀' : 'NORMAL',
        activeTopPlayer: telemetry.active_players[0]?.name,
      };
    }

    // Default / Casual view
    return {
      matchId: telemetry.match_id,
      sport: telemetry.sport,
      ballSpeedKmh: Math.round(telemetry.ball.speed_kmh),
      activePlayersSummary: telemetry.active_players.map((p) => p.name || p.player_id),
    };
  }
}
