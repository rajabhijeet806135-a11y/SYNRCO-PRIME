import pytest
from app.subsystems.persona.persona_engine import PersonaEngine, QuizAnswers
from app.subsystems.persona.behavioral_classifier import BehavioralClassifier, UserSessionTelemetry
from app.datasets.dataset3_gamification import PersonaConfidenceScores
from app.subsystems.persona.persona_router import PersonaRouter
from app.datasets.dataset2_events import SAMPLE_CONTEXTUAL_EVENTS

def test_layer1_onboarding_quiz():
    # Hardcore fan profile
    quiz_hardcore = QuizAnswers(
        q1_viewing_style="deep_stats",
        q2_sports_knowledge="expert",
        q3_primary_device="smart_tv"
    )
    result = PersonaEngine.process_onboarding_quiz(quiz_hardcore)
    assert result["recommended_persona"] == "HARDCORE"
    assert result["confidence_scores"].hardcore > 0.6

    # In-Stadium profile
    quiz_stadium = QuizAnswers(
        q1_viewing_style="relaxed_fun",
        q2_sports_knowledge="intermediate",
        q3_primary_device="in_stadium"
    )
    result_stadium = PersonaEngine.process_onboarding_quiz(quiz_stadium)
    assert result_stadium["recommended_persona"] == "STADIUM"

def test_layer2_behavioral_inference():
    base_scores = PersonaConfidenceScores(casual=0.5, genz=0.5, hardcore=0.2, club_member=0.2)
    telemetry = UserSessionTelemetry(
        stat_overlay_opens=8,
        tactical_view_duration_seconds=120,
        prediction_reaction_speed_ms=[4500, 3200],
        chat_messages_sent=1,
        emotes_sent=0,
        clan_lounges_visited=0,
        plain_english_help_requested=0,
        in_stadium_5g_connected=False,
        total_interactions=12
    )

    updated = BehavioralClassifier.classify(telemetry, base_scores)
    assert updated.hardcore > 0.4
    assert updated.casual < 0.5

@pytest.mark.asyncio
async def test_layer3_manual_override():
    res = await PersonaEngine.manual_override_persona(
        user_id="usr_genz_7721",
        new_persona="HARDCORE"
    )
    assert res["success"] is True
    assert res["active_persona"] == "HARDCORE"

def test_persona_router_adaptation():
    event = SAMPLE_CONTEXTUAL_EVENTS[0]  # DRS LBW review
    
    casual_view = PersonaRouter.adapt_contextual_event(event, "CASUAL")
    assert casual_view.ui_mode == "SIMPLIFIED_EXPLANATION"
    assert "hit the stumps" in casual_view.content["headline"]

    genz_view = PersonaRouter.adapt_contextual_event(event, "GEN_Z")
    assert genz_view.ui_mode == "RAPID_MICRO_PREDICTION"
    assert "OUT or NOT OUT" in genz_view.content["headline"]

    hardcore_view = PersonaRouter.adapt_contextual_event(event, "HARDCORE")
    assert hardcore_view.ui_mode == "TACTICAL_DEEP_DIVE"
    assert "xWicket" in hardcore_view.content["headline"]
