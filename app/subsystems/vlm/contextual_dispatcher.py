import time
from typing import Optional, Dict, Any, List
from app.config import SportType
from app.datasets.dataset2_events import ContextualEventData, PersonaPrompts
from app.subsystems.vlm.inference_pool import VlmTacticalInference
from app.core.events import event_bus, Topics

class ContextualDispatcher:
    _instance: Optional['ContextualDispatcher'] = None

    @classmethod
    def get_instance(cls) -> 'ContextualDispatcher':
        if cls._instance is None:
            cls._instance = ContextualDispatcher()
        return cls._instance

    async def handle_inference(self, inference: VlmTacticalInference, sport: SportType) -> Optional[ContextualEventData]:
        if not inference.is_dead_time and not inference.detected_event:
            return None

        event_id = f"EVT_{inference.detected_event or 'DEAD_TIME'}_{str(int(time.time()))[-4:]}"
        duration = inference.suggested_dead_time_duration_seconds or 30

        prompts = PersonaPrompts(
            casual="What do you think the decision will be?",
            genz="Quick Vote: What happens next? 🔥⚡ (100 $SYNC)",
            hardcore="Historical Probability Model: 74% conversion rate",
            club_member="Clan Rally: Boost your clan leaderboard tally now!",
            stadium="Stadium Screen: Watch the live video review replay",
            broadcaster="Official Matchday Poll: Vote on the stream"
        )
        options: List[str] = ["Yes", "No"]
        odds: Dict[str, float] = {"Yes": 1.85, "No": 1.95}

        if inference.detected_event == "DRS_LBW_REVIEW":
            prompts = PersonaPrompts(
                casual="Will the ball hit the stumps? (Yes / No)",
                genz="DRS Verdict: OUT or NOT OUT? 🔥 (100 $SYNC at stake)",
                hardcore="Predicted Impact: In Line / Outside Off (xWicket: 0.72)",
                club_member="Clan Clash: Stand with your team!",
                stadium="Stadium AR: Hawkeye replay on big screen",
                broadcaster="HawkEye Broadcast Overlay Active"
            )
            options = ["OUT", "NOT OUT", "UMPIRE'S CALL"]
            odds = {"OUT": 2.1, "NOT OUT": 1.65, "UMPIRE'S CALL": 3.8}

        elif inference.detected_event == "VAR_PENALTY_CHECK":
            prompts = PersonaPrompts(
                casual="Did the referee make the right call?",
                genz="VAR Decision: PENALTY or PLAY ON? ⚽⚡",
                hardcore="VAR Review Probability: 0.82 Penalty Given | xG: 0.79",
                club_member="Clan War: Win glory for your club!",
                stadium="Enjoy 20% discount on concessions during VAR pause",
                broadcaster="Nike Clutch Moment: Instant Spot-Kick Poll"
            )
            options = ["PENALTY_GIVEN", "NO_PENALTY"]
            odds = {"PENALTY_GIVEN": 1.5, "NO_PENALTY": 2.6}

        context_event = ContextualEventData(
            event_id=event_id,
            match_id=inference.match_id,
            sport=sport,
            event_type=inference.detected_event or "MATCH_STOPPAGE",
            is_dead_time=inference.is_dead_time,
            estimated_dead_time_seconds=duration,
            contextual_narrative=inference.ai_narrative,
            prompts_generated=prompts,
            prediction_options=options,
            odds=odds,
            timestamp_ms=inference.timestamp_ms
        )

        dumped = context_event.model_dump() if hasattr(context_event, 'model_dump') else context_event.dict()
        await event_bus.publish(Topics.CONTEXTUAL_EVENT, dumped, source="contextual_dispatcher")
        if inference.is_dead_time:
            await event_bus.publish(Topics.DEAD_TIME_DETECTED, dumped, source="contextual_dispatcher")

        return context_event

contextual_dispatcher = ContextualDispatcher.get_instance()
