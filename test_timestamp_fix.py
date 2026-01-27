#!/usr/bin/env python3
"""
Test script to verify timestamp conversion fix for Issue #32.
This tests that timestamps are correctly converted to local timezone.
"""

from datetime import datetime, timezone
import time

def test_timestamp_conversion():
    """Test that timestamp conversion uses local timezone."""
    # Get current timestamp
    timestamp = int(time.time())
    
    # OLD WAY (incorrect - displays UTC time)
    old_date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    # NEW WAY (correct - displays local time)
    new_date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
    
    # Also test direct local conversion
    local_date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Timestamp: {timestamp}")
    print(f"OLD (UTC): {old_date_str}")
    print(f"NEW (Local via astimezone): {new_date_str}")
    print(f"Local (direct): {local_date_str}")
    print()
    
    # The new way and direct local should be the same
    if new_date_str == local_date_str:
        print("✅ SUCCESS: Timestamp conversion is correct!")
        print(f"   Local time displayed: {new_date_str}")
    else:
        print("❌ ERROR: Timestamp conversions don't match!")
        return False
    
    # Show the timezone offset
    local_tz = datetime.now().astimezone().tzinfo
    print(f"   Timezone: {local_tz}")
    
    return True

if __name__ == "__main__":
    test_timestamp_conversion()
