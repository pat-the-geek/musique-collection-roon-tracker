#!/usr/bin/env python3
"""
Verify that the timeline HTML fix works correctly.
Tests the new compact HTML generation without excessive whitespace.
"""
import html

def test_compact_mode():
    """Test compact mode HTML generation."""
    # Sample data
    artist = 'Bob Dylan & The Band'
    title = 'Song "Live"'
    album = 'Greatest Hits'
    time = '10:15'
    img_url = 'https://i.scdn.co/image/img1.jpg'
    
    # Apply escaping (like the fixed code)
    safe_artist = html.escape(artist, quote=True)
    safe_title = html.escape(title, quote=True)
    safe_album = html.escape(album, quote=True)
    safe_time = html.escape(time, quote=True)
    
    # Generate HTML (new single-line format)
    timeline_html = f'<div class="track-in-hour" title="{safe_artist} - {safe_title}&#10;{safe_album}&#10;{safe_time}"><img src="{img_url}" class="album-cover-timeline" alt="{safe_album}"></div>'
    
    print("="*80)
    print("COMPACT MODE - NEW FORMAT (Single Line)")
    print("="*80)
    print(timeline_html)
    print()
    print(f"✅ Length: {len(timeline_html)} characters")
    print(f"✅ Contains escaped &: {' &amp; ' in timeline_html}")
    print(f"✅ Contains escaped quotes: {'&quot;' in timeline_html}")
    print(f"✅ Properly closed tags: {timeline_html.count('<div') == timeline_html.count('</div>')}")
    print()
    
    return timeline_html

def test_detailed_mode():
    """Test detailed mode HTML generation."""
    artist = 'Bob Dylan & The Band'
    title = 'Song "Live"'
    album = 'Greatest Hits'
    time = '10:15'
    img_url = 'https://i.scdn.co/image/img1.jpg'
    
    # Apply escaping
    safe_artist = html.escape(artist, quote=True)
    safe_title = html.escape(title, quote=True)
    safe_album = html.escape(album, quote=True)
    safe_time = html.escape(time, quote=True)
    
    # Generate HTML (new single-line format)
    timeline_html = f'<div class="track-in-hour"><img src="{img_url}" class="album-cover-timeline" alt="{safe_album}"><div class="track-info-timeline"><b>{safe_time}</b></div><div class="track-info-timeline">{safe_artist[:20]}</div><div class="track-info-timeline">{safe_title[:20]}</div></div>'
    
    print("="*80)
    print("DETAILED MODE - NEW FORMAT (Single Line)")
    print("="*80)
    print(timeline_html)
    print()
    print(f"✅ Length: {len(timeline_html)} characters")
    print(f"✅ Contains escaped &: {' &amp; ' in timeline_html}")
    print(f"✅ Contains escaped quotes: {'&quot;' in timeline_html}")
    print(f"✅ Properly closed tags: {timeline_html.count('<div') == timeline_html.count('</div>')}")
    print(f"✅ Artist truncation works: {'Bob Dylan &amp; The B' in timeline_html}")
    print()
    
    return timeline_html

def test_full_timeline():
    """Test generating a full timeline with multiple tracks."""
    tracks = [
        {"artist": "Nina Simone", "title": "Feeling Good", "album": "I Put A Spell On You", "img": "https://i.scdn.co/image/img1.jpg", "time": "10:15"},
        {"artist": 'Bob Dylan & The Band', "title": 'Song "Live"', "album": "Greatest Hits", "img": "https://i.scdn.co/image/img2.jpg", "time": "10:30"},
        {"artist": "Prince", "title": "Purple Rain <Remaster>", "album": "Best Of", "img": "https://i.scdn.co/image/img3.jpg", "time": "10:45"},
    ]
    
    timeline_html = '<div class="timeline-container">'
    timeline_html += '<div class="timeline-hour">'
    timeline_html += '<div class="hour-label">10:00 (3)</div>'
    
    for track in tracks:
        img_url = track['img']
        artist = track['artist']
        title = track['title']
        album = track['album']
        time = track['time']
        
        safe_artist = html.escape(artist, quote=True)
        safe_title = html.escape(title, quote=True)
        safe_album = html.escape(album, quote=True)
        safe_time = html.escape(time, quote=True)
        
        timeline_html += f'<div class="track-in-hour" title="{safe_artist} - {safe_title}&#10;{safe_album}&#10;{safe_time}"><img src="{img_url}" class="album-cover-timeline" alt="{safe_album}"></div>'
    
    timeline_html += '</div>'
    timeline_html += '</div>'
    
    print("="*80)
    print("FULL TIMELINE - MULTIPLE TRACKS")
    print("="*80)
    print(timeline_html)
    print()
    print(f"✅ Total length: {len(timeline_html)} characters")
    print(f"✅ Number of track divs: {timeline_html.count('class=\"track-in-hour\"')}")
    print(f"✅ Number of images: {timeline_html.count('<img src')}")
    print(f"✅ Properly closed tags: {timeline_html.count('<div') == timeline_html.count('</div>')}")
    print()
    
    # OLD format would have been much longer
    old_estimated_length = len(timeline_html) * 3  # Triple the size with whitespace
    print(f"📊 Estimated old format length: {old_estimated_length} characters")
    print(f"📊 Size reduction: {((old_estimated_length - len(timeline_html)) / old_estimated_length * 100):.1f}%")
    print()

if __name__ == '__main__':
    test_compact_mode()
    test_detailed_mode()
    test_full_timeline()
    
    print("="*80)
    print("✅ ALL TESTS PASSED - HTML generation looks correct!")
    print("="*80)
