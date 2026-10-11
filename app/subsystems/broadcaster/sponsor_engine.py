from typing import Dict, Any, List
from pydantic import BaseModel

class SponsoredMoment(BaseModel):
    sponsor_id: str
    brand_name: str
    campaign_title: str
    banner_url: str
    cta_text: str
    reward_bonus_multiplier: float

class SponsorEngine:
    SPONSORED_CAMPAIGNS: Dict[str, SponsoredMoment] = {
        "nike_speed": SponsoredMoment(
            sponsor_id="sp_nike_01",
            brand_name="Nike Football",
            campaign_title="Nike Speed Prediction: Will this sprint exceed 33 km/h?",
            banner_url="https://assets.syncroprime.io/sponsors/nike_sprint.png",
            cta_text="Claim Nike Fan Badge & 2x $SYNC",
            reward_bonus_multiplier=2.0
        ),
        "hawkeye_precision": SponsoredMoment(
            sponsor_id="sp_hawkeye_02",
            brand_name="HawkEye Innovations",
            campaign_title="HawkEye DRS Precision Challenge",
            banner_url="https://assets.syncroprime.io/sponsors/hawkeye_precision.png",
            cta_text="Vote on Ball Impact Line",
            reward_bonus_multiplier=1.5
        )
    }

    @staticmethod
    def get_campaign(campaign_key: str) -> SponsoredMoment:
        return SponsorEngine.SPONSORED_CAMPAIGNS.get(
            campaign_key,
            SponsorEngine.SPONSORED_CAMPAIGNS["nike_speed"]
        )

    @staticmethod
    def list_campaigns() -> List[SponsoredMoment]:
        return list(SponsorEngine.SPONSORED_CAMPAIGNS.values())
