import { ContextualEventData } from '../../datasets/dataset2_events.js';
import { VlmTacticalInference } from './vlmInferencePool.js';
import { eventBus } from '../../core/events/eventBus.js';
import { TOPICS } from '../../core/events/topics.js';
import { SportType } from '../../config/index.js';

export class ContextualDispatcher {
  private static instance: ContextualDispatcher;

  private constructor() {}

  public static getInstance(): ContextualDispatcher {
    if (!ContextualDispatcher.instance) {
      ContextualDispatcher.instance = new ContextualDispatcher();
    }
    return ContextualDispatcher.instance;
  }

  /**
   * Evaluates VLM inference and dispatches actionable contextual events
   */
  public async handleInference(inference: VlmTacticalInference, sport: SportType): Promise<ContextualEventData | null> {
    if (!inference.isDeadTime && !inference.detectedEvent) {
      return null;
    }

    const eventId = `EVT_${inference.detectedEvent || 'DEAD_TIME'}_${Date.now().toString().slice(-4)}`;
    const duration = inference.suggestedDeadTimeDurationSeconds || 30;

    let prompts = {
      casual: 'What do you think the decision will be?',
      genz: 'Quick Vote: What happens next? 🔥⚡ (100 $SYNC)',
      hardcore: 'Historical Probability Model: 74% conversion rate',
      club_member: 'Clan Rally: Boost your clan leaderboard tally now!',
      stadium: 'Stadium Screen: Watch the live video review replay',
      broadcaster: 'Official Matchday Poll: Vote on the stream',
    };

    let options = ['Yes', 'No'];
    let odds = { Yes: 1.85, No: 1.95 };

    if (inference.detectedEvent === 'DRS_LBW_REVIEW') {
      prompts = {
        casual: 'Will the ball hit the stumps? (Yes / No)',
        genz: 'DRS Verdict: OUT or NOT OUT? 🔥 (100 $SYNC at stake)',
        hardcore: 'Predicted Impact: In Line / Outside Off (xWicket: 0.72)',
        club_member: 'Clan Clash: Stand with your team!',
        stadium: 'Stadium AR: Hawkeye replay on big screen',
        broadcaster: 'HawkEye Broadcast Overlay Active',
      };
      options = ['OUT', 'NOT OUT', "UMPIRE'S CALL"];
      odds = { OUT: 2.1, 'NOT OUT': 1.65, "UMPIRE'S CALL": 3.8 };
    } else if (inference.detectedEvent === 'VAR_PENALTY_CHECK') {
      prompts = {
        casual: 'Did the referee make the right call?',
        genz: 'VAR Decision: PENALTY or PLAY ON? ⚽⚡',
        hardcore: 'VAR Review Probability: 0.82 Penalty Given | xG: 0.79',
        club_member: 'Clan War: Win glory for your club!',
        stadium: 'Enjoy 20% discount on concessions during VAR pause',
        broadcaster: 'Nike Clutch Moment: Instant Spot-Kick Poll',
      };
      options = ['PENALTY_GIVEN', 'NO_PENALTY'];
      odds = { PENALTY_GIVEN: 1.5, NO_PENALTY: 2.6 };
    }

    const contextEvent: ContextualEventData = {
      event_id: eventId,
      match_id: inference.matchId,
      sport,
      event_type: inference.detectedEvent || 'MATCH_STOPPAGE',
      is_dead_time: inference.isDeadTime,
      estimated_dead_time_seconds: duration,
      contextual_narrative: inference.aiNarrative,
      prompts_generated: prompts,
      prediction_options: options,
      odds,
      timestamp_ms: inference.timestampMs,
    };

    // Publish to EventBus
    await eventBus.publish(TOPICS.CONTEXTUAL_EVENT, contextEvent, 'contextual_dispatcher');
    if (inference.isDeadTime) {
      await eventBus.publish(TOPICS.DEAD_TIME_DETECTED, contextEvent, 'contextual_dispatcher');
    }

    return contextEvent;
  }
}

export const contextualDispatcher = ContextualDispatcher.getInstance();
