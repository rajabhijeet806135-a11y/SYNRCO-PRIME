import pytest
from app.datasets.dataset1_telemetry import SAMPLE_CRICKET_TELEMETRY
from app.subsystems.vlm.inference_pool import vlm_inference_pool
from app.subsystems.vlm.contextual_dispatcher import contextual_dispatcher
from app.subsystems.vlm.highlight_generator import highlight_generator
from app.core.ttl_cache import shared_vlm_cache

@pytest.mark.asyncio
async def test_shared_vlm_pool_o1_compute():
    vlm_inference_pool.prewarm_match_pool("IND_AUS_T20_2026")
    initial_metrics = vlm_inference_pool.get_metrics()
    initial_count = initial_metrics["total_inferences"]

    # 1. First viewer inference
    res1 = await vlm_inference_pool.infer_broadcast_context("IND_AUS_T20_2026", SAMPLE_CRICKET_TELEMETRY)
    assert res1.match_id == "IND_AUS_T20_2026"
    assert vlm_inference_pool.get_metrics()["total_inferences"] == initial_count + 1

    # 2. Second viewer of the SAME match within 500ms -> Cache hit, O(1) compute!
    res2 = await vlm_inference_pool.infer_broadcast_context("IND_AUS_T20_2026", SAMPLE_CRICKET_TELEMETRY)
    assert res2.match_id == "IND_AUS_T20_2026"
    assert vlm_inference_pool.get_metrics()["total_inferences"] == initial_count + 1  # No new compute!

@pytest.mark.asyncio
async def test_contextual_dispatcher_dead_time():
    vlm_res = await vlm_inference_pool.infer_broadcast_context("IND_AUS_T20_2026", SAMPLE_CRICKET_TELEMETRY)
    vlm_res.is_dead_time = True
    vlm_res.detected_event = "DRS_LBW_REVIEW"

    evt = await contextual_dispatcher.handle_inference(vlm_res, "CRICKET")
    assert evt is not None
    assert evt.is_dead_time is True
    assert "OUT or NOT OUT" in evt.prompts_generated.genz

@pytest.mark.asyncio
async def test_ai_highlight_generator():
    clip = await highlight_generator.generate_highlight(
        match_id="MCI_RMA_UCL_2026",
        title="Haaland Rocket Volley",
        narrative="Thunderous strike from the edge of the box into top corner.",
        hype_score=96,
        crowd_db=112.4
    )
    assert clip.hype_rating == 96
    assert clip.crowd_decibel_peak == 112.4

    highlights = highlight_generator.get_highlights("MCI_RMA_UCL_2026")
    assert len(highlights) >= 1
    assert highlights[0].clip_id == clip.clip_id
