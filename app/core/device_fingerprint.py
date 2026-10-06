import hashlib
from typing import Optional
from pydantic import BaseModel

class DeviceMetadata(BaseModel):
    user_agent: Optional[str] = "unknown_ua"
    ip: Optional[str] = "127.0.0.1"
    screen_resolution: Optional[str] = "1920x1080"
    platform: Optional[str] = "web"
    language: Optional[str] = "en-US"
    timezone_offset: Optional[int] = 0
    canvas_fingerprint: Optional[str] = "standard_canvas"

class DeviceFingerprinter:
    @staticmethod
    def generate_fingerprint(meta: DeviceMetadata) -> str:
        raw = "|".join([
            meta.user_agent or "unknown_ua",
            meta.screen_resolution or "1920x1080",
            meta.platform or "web",
            meta.language or "en-US",
            str(meta.timezone_offset or 0),
            meta.canvas_fingerprint or "standard_canvas",
        ])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def extract_subnet(ip: Optional[str]) -> str:
        if not ip or ip in ("127.0.0.1", "::1", "localhost"):
            return "127.0.0.0/24"

        if "." in ip:
            parts = ip.split(".")
            if len(parts) >= 3:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

        if ":" in ip:
            parts = ip.split(":")
            if len(parts) >= 3:
                return f"{parts[0]}:{parts[1]}:{parts[2]}::/48"

        return ip
