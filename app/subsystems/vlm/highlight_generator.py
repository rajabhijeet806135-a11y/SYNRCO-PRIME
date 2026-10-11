import time
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.core.events import event_bus, Topics

class AiHighlightClip(BaseModel):
    clip_id: str
    match_id: str
    timestamp_epoch_ms: int
    duration_seconds: int
    hype_rating: int
    title: str
    ai_description: str
    thumbnail_url: str
    video_clip_url: str
    crowd_decibel_peak: float
    tags: List[str]

class HighlightGenerator:
    _instance: Optional['HighlightGenerator'] = None

    def __init__(self):
        self._highlights_by_match: Dict[str, List[AiHighlightClip]] = {}

    @classmethod
    def get_instance(cls) -> 'HighlightGenerator':
        if cls._instance is None:
            cls._instance = HighlightGenerator()
        return cls._instance

    async def generate_highlight(
        self,
        match_id: str,
        title: str,
        narrative: str,
        hype_score: int = 85,
        crowd_db: float = 104.5,
        tags: Optional[List[str]] = None
    ) -> AiHighlightClip:
        now_ms = int(time.time() * 1000)
        clip_id = f"hl_{match_id}_{now_ms}"
        clip = AiHighlightClip(
            clip_id=clip_id,
            match_id=match_id,
            timestamp_epoch_ms=now_ms,
            duration_seconds=15,
            hype_rating=min(100, max(0, hype_score)),
            title=title,
            ai_description=narrative,
            thumbnail_url=f"https://assets.syncroprime.io/highlights/{clip_id}_thumb.jpg",
            video_clip_url=f"https://stream.syncroprime.io/clips/{clip_id}.mp4",
            crowd_decibel_peak=crowd_db,
            tags=tags or ["AI_CLIP", "KEY_PLAY"]
        )

        if match_id not in self._highlights_by_match:
            self._highlights_by_match[match_id] = []
        self._highlights_by_match[match_id].insert(0, clip)

        if len(self._highlights_by_match[match_id]) > 25:
            self._highlights_by_match[match_id].pop()

        dumped = clip.model_dump() if hasattr(clip, 'model_dump') else clip.dict()
        await event_bus.publish(Topics.HIGHLIGHT_GENERATED, dumped, source="highlight_generator")

        return clip

    def get_highlights(self, match_id: str) -> List[AiHighlightClip]:
        return self._highlights_by_match.get(match_id, [])

highlight_generator = HighlightGenerator.get_instance()
