"""Test script to understand HTML rendering issue in Timeline."""
import html

# Simulate what the code does
artist = "Test Artist"
title = "Test Title"
album = "Test Album"
time = "10:30"
img_url = "https://example.com/image.jpg"

# Escape with quote=True
safe_artist = html.escape(artist, quote=True)
safe_title = html.escape(title, quote=True)
safe_album = html.escape(album, quote=True)
safe_time = html.escape(time, quote=True)

# Build HTML like in compact mode
timeline_html = f'''
<div class="track-in-hour" title="{safe_artist} - {safe_title}&#10;{safe_album}&#10;{safe_time}">
    <img src="{img_url}" class="album-cover-timeline" alt="{safe_album}">
</div>
'''

print("Generated HTML:")
print(timeline_html)
print("\n" + "="*50 + "\n")

# Build HTML like in detailed mode
timeline_html2 = f'''
<div class="track-in-hour">
    <img src="{img_url}" class="album-cover-timeline" alt="{safe_album}">
    <div class="track-info-timeline"><b>{safe_time}</b></div>
    <div class="track-info-timeline">{safe_artist[:20]}</div>
    <div class="track-info-timeline">{safe_title[:20]}</div>
</div>
'''

print("Detailed HTML:")
print(timeline_html2)
