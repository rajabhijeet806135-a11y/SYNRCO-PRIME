import asyncio
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from app.core.redis_state import InMemoryRedisState

@dataclass
class RedisNode:
    id: str
    role: str  # 'PRIMARY' | 'REPLICA'
    region: str
    is_healthy: bool
    instance: InMemoryRedisState

class SentinelPool:
    def __init__(self):
        self.primary_node_id = "node-primary-us-east"
        self.nodes: Dict[str, RedisNode] = {}
        self.sentinel_nodes = ["sentinel-1", "sentinel-2", "sentinel-3"]
        self._failover_listeners = []
        self._init_cluster()

    def _init_cluster(self):
        self.nodes[self.primary_node_id] = RedisNode(
            id=self.primary_node_id,
            role="PRIMARY",
            region="us-east",
            is_healthy=True,
            instance=InMemoryRedisState()
        )

        self.nodes["replica-1-eu-west"] = RedisNode(
            id="replica-1-eu-west",
            role="REPLICA",
            region="eu-west",
            is_healthy=True,
            instance=InMemoryRedisState()
        )

        self.nodes["replica-2-ap-south"] = RedisNode(
            id="replica-2-ap-south",
            role="REPLICA",
            region="ap-south",
            is_healthy=True,
            instance=InMemoryRedisState()
        )

        self.nodes["replica-3-us-west"] = RedisNode(
            id="replica-3-us-west",
            role="REPLICA",
            region="us-west",
            is_healthy=True,
            instance=InMemoryRedisState()
        )

    def get_primary(self) -> RedisNode:
        node = self.nodes.get(self.primary_node_id)
        if not node or not node.is_healthy:
            raise RuntimeError("[SentinelPool] No healthy Redis primary found! Failover required.")
        return node

    def get_read_replica(self, preferred_region: Optional[str] = None) -> RedisNode:
        replicas = [n for n in self.nodes.values() if n.role == "REPLICA" and n.is_healthy]
        if not replicas:
            return self.get_primary()

        if preferred_region:
            for r in replicas:
                if r.region == preferred_region:
                    return r

        return random.choice(replicas)

    async def trigger_failover(self, reason: str = "Simulated Hardware Failure") -> Dict[str, Any]:
        """
        Simulate Primary Node Crash and Automatic Sentinel Failover (< 5 sec SLA)
        """
        start_time = time.time()
        old_primary_id = self.primary_node_id
        old_primary = self.nodes.get(old_primary_id)
        if old_primary:
            old_primary.is_healthy = False
            print(f"[SentinelPool] Primary {old_primary_id} failed! ({reason}). Sentinels initiating quorum election...")

        quorum = self.sentinel_nodes[:2]
        candidates = [n for n in self.nodes.values() if n.id != old_primary_id and n.is_healthy]
        if not candidates:
            raise RuntimeError("[SentinelPool] Split-brain critical: No healthy replicas available for promotion!")

        promoted = candidates[0]
        promoted.role = "PRIMARY"
        self.primary_node_id = promoted.id

        duration_ms = int((time.time() - start_time) * 1000) + 110  # Quorum consensus latency

        print(f"[SentinelPool] Failover complete! {promoted.id} ({promoted.region}) promoted to PRIMARY in {duration_ms}ms.")

        for listener in self._failover_listeners:
            listener(promoted.id)

        return {
            "old_primary": old_primary_id,
            "new_primary": promoted.id,
            "failover_duration_ms": duration_ms,
            "quorum_sentinels": quorum
        }

    def on_failover(self, callback):
        self._failover_listeners.append(callback)

    def get_topology(self) -> List[Dict[str, Any]]:
        return [
            {"id": n.id, "role": n.role, "region": n.region, "is_healthy": n.is_healthy}
            for n in self.nodes.values()
        ]

sentinel_pool = SentinelPool()
