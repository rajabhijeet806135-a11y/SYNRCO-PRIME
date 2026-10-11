#!/usr/bin/env python3
"""
Runs test_angles_positions suite using standard python asyncio runner.
"""
import asyncio
import sys
import os

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tests.test_angles_positions import (
    test_get_all_matches,
    test_get_camera_angles_multi_sport,
    test_hawkeye_drs_angles,
    test_player_positions_and_orientations,
    test_tactical_moments_camera_linkage,
    test_record_telemetry_frame_write
)

async def main():
    print("Running SYNCRO PRIME Angles & Positions Backend Tests...")
    
    await test_get_all_matches()
    print("  [PASS] test_get_all_matches")
    
    await test_get_camera_angles_multi_sport()
    print("  [PASS] test_get_camera_angles_multi_sport")
    
    await test_hawkeye_drs_angles()
    print("  [PASS] test_hawkeye_drs_angles")
    
    await test_player_positions_and_orientations()
    print("  [PASS] test_player_positions_and_orientations")
    
    await test_tactical_moments_camera_linkage()
    print("  [PASS] test_tactical_moments_camera_linkage")
    
    await test_record_telemetry_frame_write()
    print("  [PASS] test_record_telemetry_frame_write")
    
    print("\nALL 6 ASYNC BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
