import asyncio
import time
import random
from typing import Dict, Any, Optional
from app.datasets.dataset1_telemetry import SAMPLE_CRICKET_TELEMETRY, SAMPLE_FOOTBALL_TELEMETRY, SAMPLE_BASKETBALL_TELEMETRY
from app.subsystems.telemetry.pipeline import telemetry_pipeline
from app.subsystems.vlm.inference_pool import vlm_inference_pool
from app.subsystems.vlm.contextual_dispatcher import contextual_dispatcher
from app.subsystems.crowd.decibel_engine import crowd_decibel_engine
from app.subsystems.settlement.prediction_manager import prediction_manager
from app.subsystems.settlement.settlement_worker import settlement_worker

class MatchSimulator:
    """
    Real-Time Multi-Sport Live Broadcast Simulation Engine
    Simulates high-frequency optical tracking, contextual dead times, VLM inference,
    crowd decibels, and settlement cycles across Cricket, Football, and Basketball.
    """
    _instance: Optional['MatchSimulator'] = None

    def __init__(self):
        self._is_running = False
        self._sim_task: Optional[asyncio.Task] = None
        self._frame_count = 0

    @classmethod
    def get_instance(cls) -> 'MatchSimulator':
        if cls._instance is None:
            cls._instance = MatchSimulator()
        return cls._instance

    def start(self):
        if not self._is_running:
            self._is_running = True
            self._sim_task = asyncio.create_task(self._simulation_loop())
            print("[MatchSimulator] Live multi-sport simulation engine started.")

    def stop(self):
        self._is_running = False
        if self._sim_task:
            self._sim_task.cancel()
        print("[MatchSimulator] Simulation engine stopped.")

    async def _simulation_loop(self):
        # Pre-warm VLM inference pools
        vlm_inference_pool.prewarm_match_pool("IND_AUS_T20_2026")
        vlm_inference_pool.prewarm_match_pool("MCI_RMA_UCL_2026")
        vlm_inference_pool.prewarm_match_pool("LAL_GSW_NBA_2026")

        while self._is_running:
            try:
                self._frame_count += 1
                now_ms = int(time.time() * 1000)

                # 1. Cricket Simulation Step
                cricket_frame = SAMPLE_CRICKET_TELEMETRY.model_copy(deep=True) if hasattr(SAMPLE_CRICKET_TELEMETRY, 'model_copy') else SAMPLE_CRICKET_TELEMETRY.copy(deep=True)
                cricket_frame.timestamp_ms = now_ms
                cricket_frame.frame_idx = 84000 + self._frame_count
                cricket_frame.ball.speed_kmh = round(138.0 + random.uniform(0, 14), 1)
                await telemetry_pipeline.ingest_frame(cricket_frame)

                # Shared VLM match broadcast inference
                vlm_res = await vlm_inference_pool.infer_broadcast_context("IND_AUS_T20_2026", cricket_frame)
                await contextual_dispatcher.handle_inference(vlm_res, "CRICKET")

                # 2. Football Simulation Step
                football_frame = SAMPLE_FOOTBALL_TELEMETRY.model_copy(deep=True) if hasattr(SAMPLE_FOOTBALL_TELEMETRY, 'model_copy') else SAMPLE_FOOTBALL_TELEMETRY.copy(deep=True)
                football_frame.timestamp_ms = now_ms
                football_frame.frame_idx = 120000 + self._frame_count
                football_frame.ball.speed_kmh = round(65.0 + random.uniform(0, 45), 1)
                await telemetry_pipeline.ingest_frame(football_frame)

                # 3. Basketball Simulation Step
                basketball_frame = SAMPLE_BASKETBALL_TELEMETRY.model_copy(deep=True) if hasattr(SAMPLE_BASKETBALL_TELEMETRY, 'model_copy') else SAMPLE_BASKETBALL_TELEMETRY.copy(deep=True)
                basketball_frame.timestamp_ms = now_ms
                basketball_frame.frame_idx = 99000 + self._frame_count
                await telemetry_pipeline.ingest_frame(basketball_frame)

                # 4. Crowd Decibel Fluctuation
                await crowd_decibel_engine.record_cheer("IND_AUS_T20_2026", "sim_user", intensity=random.randint(1, 5))

                # Periodic simulation sleep (simulate 2-5Hz background cadence)
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MatchSimulator] Error in simulation loop: {e}")
                await asyncio.sleep(1.0)

match_simulator = MatchSimulator.get_instance()
