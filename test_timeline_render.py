#!/usr/bin/env python3
"""
Test script to reproduce the Timeline rendering issue.
"""
import html

def generate_test_html():
    """Generate HTML similar to what the timeline does."""
    
    # Simulate track data with various special characters
    tracks = [
        {"artist": "Nina Simone", "title": "Feeling Good", "album": "I Put A Spell On You", "img": "https://i.scdn.co/image/img1.jpg"},
        {"artist": 'Bob Dylan & The Band', "title": 'Song "Live"', "album": "Greatest Hits", "img": "https://i.scdn.co/image/img2.jpg"},
        {"artist": "Prince", "title": "Purple Rain <Remaster>", "album": "Best Of", "img": "https://i.scdn.co/image/img3.jpg"},
        {"artist": "David Bowie", "title": "Space Oddity", "album": "Space Oddity", "img": "https://i.scdn.co/image/img4.jpg"},
    ]
    
    timeline_html = '<div class="timeline-container">'
    
    for hour in [10, 11]:
        timeline_html += f'<div class="timeline-hour">'
        timeline_html += f'<div class="hour-label">{hour:02d}:00 ({len(tracks)})</div>'
        
        for track in tracks:
            img_url = track['img']
            artist = track['artist']
            title = track['title']
            album = track['album']
            time = f"{hour}:15"
            
            # WITH escaping (current code)
            safe_artist = html.escape(artist, quote=True)
            safe_title = html.escape(title, quote=True)
            safe_album = html.escape(album, quote=True)
            safe_time = html.escape(time, quote=True)
            
            timeline_html += f'''
                        <div class="track-in-hour" title="{safe_artist} - {safe_title}&#10;{safe_album}&#10;{safe_time}">
                            <img src="{img_url}" class="album-cover-timeline" alt="{safe_album}">
                        </div>
                        '''
        
        timeline_html += '</div>'
    
    timeline_html += '</div>'
    
    return timeline_html

if __name__ == '__main__':
    html_output = generate_test_html()
    print("="*80)
    print("GENERATED HTML")
    print("="*80)
    print(html_output)
    print("\n")
    print("="*80)
    print(f"Total length: {len(html_output)} characters")
    print("="*80)
    
    # Check for any issues
    if '<img src' in html_output and '</div>' in html_output:
        print("✅ HTML structure looks correct")
    else:
        print("❌ HTML structure may have issues")
    
    # Count how many img tags
    img_count = html_output.count('<img src')
    print(f"✅ Found {img_count} img tags")
