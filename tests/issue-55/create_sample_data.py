#!/usr/bin/env python3
"""
Create sample data for testing the Timeline view.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

# Create sample track data
def create_sample_roon_data():
    """Generate sample chk-roon.json data for testing Timeline view."""
    
    sample_tracks = []
    base_date = datetime(2026, 1, 28)
    
    # Sample albums with special characters to test HTML escaping
    albums = [
        {"artist": "Nina Simone", "title": "Feeling Good", "album": "I Put A Spell On You", 
         "spotify_img": "https://i.scdn.co/image/ab67616d0000b273e8b066f70c206551210d902b",
         "lastfm_img": "https://lastfm.freetls.fastly.net/i/u/300x300/2ca21c7d4febd3042545d1afece307f1.jpg"},
        {"artist": 'Bob Dylan & The Band', "title": 'Song "Live"', "album": "Greatest Hits",
         "spotify_img": "https://i.scdn.co/image/ab67616d0000b273b2cf19034c2a6f7582cae8b8",
         "lastfm_img": "https://lastfm.freetls.fastly.net/i/u/300x300/996c38a7ed03c965450371e7d68255c2.gif"},
        {"artist": "Prince", "title": "Purple Rain <Remaster>", "album": "Best Of",
         "spotify_img": "https://i.scdn.co/image/ab67616d0000b27302cb21292aeb764d270b85c0",
         "lastfm_img": "https://lastfm.freetls.fastly.net/i/u/300x300/3b54885952161aaea4ce2965d28a5c11.jpg"},
        {"artist": "David Bowie", "title": "Space Oddity", "album": "Space Oddity",
         "spotify_img": "https://i.scdn.co/image/ab67616d0000b273d9c20a78df6b65574835c4c0",
         "lastfm_img": "https://lastfm.freetls.fastly.net/i/u/300x300/abc123.jpg"},
        {"artist": "The Beatles", "title": "Hey Jude", "album": "1967-1970",
         "spotify_img": "https://i.scdn.co/image/ab67616d0000b273876c7eed71fdfe29697bcdcd",
         "lastfm_img": "https://lastfm.freetls.fastly.net/i/u/300x300/def456.jpg"},
    ]
    
    # Generate tracks for hours 10-15
    track_id = 1
    for hour in range(10, 16):
        # Random number of tracks per hour (2-4)
        num_tracks = (hour % 3) + 2
        for i in range(num_tracks):
            album_data = albums[track_id % len(albums)]
            
            # Create timestamp for this track
            minute = (i * 12) % 60  # Spread across the hour
            track_time = base_date.replace(hour=hour, minute=minute, second=0)
            
            track = {
                "timestamp": int(track_time.timestamp()),
                "date": track_time.strftime("%Y-%m-%d %H:%M"),
                "artist": album_data["artist"],
                "title": album_data["title"],
                "album": album_data["album"],
                "loved": False,
                "artist_spotify_image": album_data["spotify_img"],
                "album_spotify_image": album_data["spotify_img"],
                "album_lastfm_image": album_data["lastfm_img"],
                "source": "roon",
                "ai_info": f"Sample AI info for {album_data['album']}"
            }
            
            sample_tracks.append(track)
            track_id += 1
    
    return sample_tracks

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    data_dir = Path("data/history")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample data
    tracks = create_sample_roon_data()
    
    # Save to file
    output_file = data_dir / "chk-roon.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created sample data: {output_file}")
    print(f"📊 Generated {len(tracks)} tracks")
    print(f"📅 Date: 2026-01-28")
    print(f"🕐 Hours covered: 10:00 - 15:00")
    print()
    print("Sample tracks:")
    for i, track in enumerate(tracks[:3]):
        print(f"  {i+1}. {track['date']} - {track['artist']} - {track['title']}")
    print(f"  ... and {len(tracks) - 3} more")
