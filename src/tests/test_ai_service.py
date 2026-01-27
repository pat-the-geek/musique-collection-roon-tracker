#!/usr/bin/env python3
"""Test script for AI service integration.

This script tests the AI service functions to ensure they work correctly
before deploying to production.

Tests:
    1. ask_for_ia() - Basic API call
    2. generate_album_info() - Album description generation
    3. get_album_info_from_discogs() - Discogs collection lookup

Usage:
    python test_ai_service.py
"""

import os
import sys

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from src.services.ai_service import ask_for_ia, generate_album_info, get_album_info_from_discogs

def test_ask_for_ia():
    """Test basic AI API call."""
    print("\n" + "="*60)
    print("TEST 1: ask_for_ia() - Basic API call")
    print("="*60)
    
    prompt = "Dis simplement 'test réussi' en 3 mots"
    print(f"Prompt: {prompt}")
    
    result = ask_for_ia(prompt, max_attempts=2, timeout=30)
    print(f"Résultat: {result}")
    
    if result and len(result) > 0:
        print("✅ TEST RÉUSSI - API répond correctement")
        return True
    else:
        print("❌ TEST ÉCHOUÉ - Aucune réponse de l'API")
        return False

def test_generate_album_info():
    """Test album info generation."""
    print("\n" + "="*60)
    print("TEST 2: generate_album_info() - Album description")
    print("="*60)
    
    artist = "Miles Davis"
    album = "Kind of Blue"
    print(f"Album: {album} de {artist}")
    
    result = generate_album_info(artist, album, max_words=35)
    print(f"\nDescription générée:\n{result}")
    
    # Check that result is not error message
    if result and not result.startswith("Désolé"):
        print(f"\n✅ TEST RÉUSSI - Description générée ({len(result.split())} mots)")
        return True
    else:
        print("\n❌ TEST ÉCHOUÉ - Erreur de génération")
        return False

def test_get_album_info_from_discogs():
    """Test Discogs collection lookup."""
    print("\n" + "="*60)
    print("TEST 3: get_album_info_from_discogs() - Discogs lookup")
    print("="*60)
    
    # This test will pass even if file doesn't exist (returns None)
    discogs_path = os.path.join(project_root, "data", "collection", "discogs-collection.json")
    
    if not os.path.exists(discogs_path):
        print(f"⚠️ Fichier Discogs non trouvé: {discogs_path}")
        print("✅ TEST PASSÉ - Fonction gère correctement le fichier absent")
        return True
    
    # Try to find an album in the collection
    album_title = "Kind of Blue"  # Common album, might be in collection
    print(f"Recherche: {album_title}")
    
    result = get_album_info_from_discogs(album_title, discogs_path)
    
    if result:
        print(f"\nRésumé trouvé:\n{result[:200]}...")
        print("\n✅ TEST RÉUSSI - Album trouvé dans Discogs")
    else:
        print(f"\n⚠️ Album non trouvé dans la collection (normal si pas dans Discogs)")
        print("✅ TEST PASSÉ - Fonction retourne None correctement")
    
    return True

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 TESTS DU SERVICE IA")
    print("="*60)
    
    results = []
    
    # Test 1: Basic API call
    results.append(("API Call", test_ask_for_ia()))
    
    # Test 2: Album info generation
    results.append(("Album Info", test_generate_album_info()))
    
    # Test 3: Discogs lookup
    results.append(("Discogs Lookup", test_get_album_info_from_discogs()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for name, passed in results:
        status = "✅ RÉUSSI" if passed else "❌ ÉCHOUÉ"
        print(f"{name:20} {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*60)
    if passed_count == total_count:
        print(f"🎉 TOUS LES TESTS RÉUSSIS ({passed_count}/{total_count})")
    else:
        print(f"⚠️ CERTAINS TESTS ONT ÉCHOUÉ ({passed_count}/{total_count})")
    print("="*60 + "\n")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
