#!/usr/bin/env python3
"""
Script de test pour valider les améliorations de la version 2.2.0
Tests la recherche d'albums Spotify avec validation d'artiste et scoring.

Usage: python3 test-spotify-search-v2.2.py
"""

import sys
import os
import importlib.util

# Charger chk-roon.py comme module
chk_roon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chk-roon.py")
spec = importlib.util.spec_from_file_location("chk_roon", chk_roon_path)
chk_roon = importlib.util.module_from_spec(spec)
sys.modules["chk_roon"] = chk_roon
spec.loader.exec_module(chk_roon)

# Importer les fonctions
get_spotify_token = chk_roon.get_spotify_token
search_spotify_album_image = chk_roon.search_spotify_album_image
clean_album_name = chk_roon.clean_album_name
clean_artist_name = chk_roon.clean_artist_name
artist_matches = chk_roon.artist_matches

# Cas de test critiques
TEST_CASES = [
    {
        "artist": "Eros Ramazzotti",
        "album": "9 [Italian]",
        "description": "Album avec crochets - cas problématique principal"
    },
    {
        "artist": "Various Artists",
        "album": "Best of 2020",
        "description": "Various Artists - doit gérer les compilations"
    },
    {
        "artist": "The Beatles",
        "album": "Abbey Road",
        "description": "Album iconique - devrait avoir un score parfait"
    },
    {
        "artist": "Nina Simone",
        "album": "Pastel Blues",
        "description": "Cas de test standard"
    },
    {
        "artist": "Miles Davis",
        "album": "Kind of Blue (Remastered)",
        "description": "Album avec parenthèses"
    }
]

def test_cleaning_functions():
    """Teste les fonctions de nettoyage."""
    print("\n" + "="*80)
    print("TEST 1: FONCTIONS DE NETTOYAGE")
    print("="*80)
    
    test_albums = [
        "9 [Italian]",
        "Best of [Deluxe Edition]",
        "Album (Remastered 2024)",
        "Circlesongs (Voice)",
        "Normal Album Name"
    ]
    
    for album in test_albums:
        cleaned = clean_album_name(album)
        status = "✅" if cleaned != album else "➡️"
        print(f"{status} '{album}' → '{cleaned}'")

def test_artist_validation():
    """Teste la validation d'artiste."""
    print("\n" + "="*80)
    print("TEST 2: VALIDATION D'ARTISTE")
    print("="*80)
    
    test_pairs = [
        ("Nina Simone", "Nina Simone", True),
        ("Nina Simone", "nina simone", True),
        ("Various", "Various Artists", True),
        ("The Beatles", "Beatles", True),
        ("Eros Ramazzotti", "Madonna", False),
        ("Miles Davis", "John Coltrane", False)
    ]
    
    for artist1, artist2, expected in test_pairs:
        result = artist_matches(artist1, artist2)
        status = "✅" if result == expected else "❌"
        match_str = "✓ MATCH" if result else "✗ NO MATCH"
        print(f"{status} '{artist1}' vs '{artist2}' → {match_str} (attendu: {'MATCH' if expected else 'NO MATCH'})")

def test_spotify_searches():
    """Teste les recherches Spotify réelles."""
    print("\n" + "="*80)
    print("TEST 3: RECHERCHES SPOTIFY RÉELLES")
    print("="*80)
    
    # Récupérer le token
    print("\n🔑 Récupération du token Spotify...")
    token = get_spotify_token()
    
    if not token:
        print("❌ Impossible de récupérer le token Spotify")
        print("   Vérifiez les variables SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET dans .env")
        return False
    
    print(f"✅ Token récupéré: {token[:20]}...\n")
    
    # Tester chaque cas
    results = []
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}/{len(TEST_CASES)}: {test['description']}")
        print(f"Artiste: {test['artist']} | Album: {test['album']}")
        print(f"{'─'*80}")
        
        # Rechercher l'image
        image_url = search_spotify_album_image(token, test['artist'], test['album'])
        
        # Vérifier le résultat
        if image_url:
            print(f"\n✅ SUCCÈS - Image trouvée:")
            print(f"   {image_url}")
            results.append((test, True, image_url))
        else:
            print(f"\n❌ ÉCHEC - Aucune image trouvée")
            results.append((test, False, None))
    
    # Résumé final
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n✅ Réussis: {success_count}/{total_count} ({success_rate:.1f}%)")
    print(f"❌ Échoués: {total_count - success_count}/{total_count}\n")
    
    for test, success, url in results:
        status = "✅" if success else "❌"
        print(f"{status} {test['artist']} - {test['album']}")
    
    return success_count == total_count

def main():
    """Point d'entrée principal."""
    print("\n" + "="*80)
    print("🧪 TEST DE LA VERSION 2.2.0 - AMÉLIORATIONS SPOTIFY SEARCH")
    print("="*80)
    
    try:
        # Test 1: Nettoyage
        test_cleaning_functions()
        
        # Test 2: Validation d'artiste
        test_artist_validation()
        
        # Test 3: Recherches réelles
        all_passed = test_spotify_searches()
        
        # Conclusion
        print("\n" + "="*80)
        if all_passed:
            print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        else:
            print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("   Vérifiez les logs ci-dessus pour plus de détails")
        print("="*80 + "\n")
        
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
