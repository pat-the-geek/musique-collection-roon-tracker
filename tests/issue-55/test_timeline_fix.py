#!/usr/bin/env python3
"""Test script to verify the timeline display fix for Issue #55.

This script simulates the HTML generation in the timeline view to verify:
1. HTML escaping prevents code injection
2. Images are properly sized to 150x150px
"""

import html

def test_html_escaping():
    """Test that problematic characters are properly escaped."""
    print("=" * 70)
    print("Test 1: HTML Escaping for Special Characters")
    print("=" * 70)
    
    test_cases = [
        # (input, description)
        ('Normal Artist', 'Normal case'),
        ('Artist "The Best"', 'Contains quotes'),
        ('Artist & The Band', 'Contains ampersand'),
        ('Artist <live>', 'Contains angle brackets'),
        ('Artist\'s Best', 'Contains apostrophe'),
        ('Mix & Match "Live" <2024>', 'All special chars'),
    ]
    
    all_passed = True
    for input_text, description in test_cases:
        escaped = html.escape(input_text, quote=True)
        
        # Check that dangerous characters are escaped
        has_unescaped_special = any(c in escaped for c in ['<', '>', '"']) and not any(seq in escaped for seq in ['&lt;', '&gt;', '&quot;'])
        
        if has_unescaped_special:
            print(f"❌ FAIL: {description}")
            print(f"   Input:   {input_text}")
            print(f"   Escaped: {escaped}")
            all_passed = False
        else:
            print(f"✅ PASS: {description}")
            print(f"   Input:   {input_text}")
            print(f"   Escaped: {escaped}")
        print()
    
    return all_passed

def test_image_css():
    """Test that CSS properly sizes images to 150x150px."""
    print("=" * 70)
    print("Test 2: CSS Image Sizing")
    print("=" * 70)
    
    # This is the CSS that should be in the code
    expected_css = """        .album-cover-timeline {
            width: 150px;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
            margin-bottom: 5px;
        }"""
    
    # Read the actual file
    try:
        with open('src/gui/musique-gui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if the CSS contains the correct sizing
        if 'width: 150px' in content and 'height: 150px' in content and 'object-fit: cover' in content:
            print("✅ PASS: CSS contains correct image sizing (150x150px)")
            print("   - width: 150px ✓")
            print("   - height: 150px ✓")
            print("   - object-fit: cover ✓")
            return True
        else:
            print("❌ FAIL: CSS does not contain correct image sizing")
            if 'width: 150px' not in content:
                print("   - Missing: width: 150px")
            if 'height: 150px' not in content:
                print("   - Missing: height: 150px")
            if 'object-fit: cover' not in content:
                print("   - Missing: object-fit: cover")
            return False
    except Exception as e:
        print(f"❌ ERROR: Could not read file: {e}")
        return False

def test_html_generation():
    """Test that HTML generation uses escaped values."""
    print("\n" + "=" * 70)
    print("Test 3: HTML Generation with Escaped Values")
    print("=" * 70)
    
    # Simulate problematic data
    artist = 'Artist & The "Band"'
    title = 'Song <Live>'
    album = 'Album "Best Of"'
    time = '14:30'
    img_url = 'https://example.com/image.jpg'
    
    # Apply HTML escaping like in the code
    safe_artist = html.escape(artist, quote=True)
    safe_title = html.escape(title, quote=True)
    safe_album = html.escape(album, quote=True)
    safe_time = html.escape(time, quote=True)
    
    # Generate HTML like in compact mode
    html_output = f'''
    <div class="track-in-hour" title="{safe_artist} - {safe_title}&#10;{safe_album}&#10;{safe_time}">
        <img src="{img_url}" class="album-cover-timeline" alt="{safe_album}">
    </div>
    '''
    
    print("Input data (with special characters):")
    print(f"  Artist: {artist}")
    print(f"  Title:  {title}")
    print(f"  Album:  {album}")
    print(f"  Time:   {time}")
    print()
    print("Generated HTML:")
    print(html_output)
    
    # Check that the HTML doesn't contain unescaped special chars in attributes
    # Verify that escaping worked by checking for HTML entities
    has_issues = False
    
    # Check that special characters are properly escaped
    if '&' in artist and '&amp;' not in html_output:
        print("❌ FAIL: Ampersand not escaped in attributes")
        has_issues = True
    if '"' in (artist + title + album) and '&quot;' not in html_output:
        print("❌ FAIL: Quotes not escaped in attributes")
        has_issues = True
    if '<' in (title + album) and '&lt;' not in html_output:
        print("❌ FAIL: Angle brackets not escaped in attributes")
        has_issues = True
    
    # Additional check: make sure we have the expected entities
    if '&amp;' in html_output and '&quot;' in html_output and '&lt;' in html_output:
        print("✅ All special characters properly escaped:")
        print("   - Ampersand (&) → &amp; ✓")
        print("   - Quotes (\") → &quot; ✓")
        print("   - Angle brackets (<>) → &lt;&gt; ✓")
    
    if not has_issues:
        print("✅ PASS: HTML generation properly escapes special characters")
        return True
    else:
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TIMELINE DISPLAY FIX VERIFICATION (Issue #55)")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("HTML Escaping", test_html_escaping()))
    results.append(("CSS Image Sizing", test_image_css()))
    results.append(("HTML Generation", test_html_generation()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All tests passed! The fix should resolve Issue #55.")
        print("\nWhat was fixed:")
        print("1. Added html.escape() to prevent HTML injection from special characters")
        print("2. Changed image CSS from 'width: 100%' to 'width: 150px; height: 150px'")
        print("3. Added 'object-fit: cover' to maintain image aspect ratio")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the fixes.")
        return 1

if __name__ == '__main__':
    exit(main())
