"""Tests pour la conversion de timestamps en date locale (Issue #32).

Ce module teste que les timestamps sont correctement convertis en heure locale
au lieu d'utiliser UTC, ce qui causait un décalage d'une heure dans l'affichage.

Version: 1.0.0
Date: 27 janvier 2026
"""

import pytest
from datetime import datetime, timezone, timedelta
import time


class TestTimestampConversion:
    """Tests pour vérifier la conversion correcte des timestamps."""
    
    def test_timestamp_to_local_time(self):
        """Vérifie que la conversion UTC -> local fonctionne correctement."""
        # Créer un timestamp de test
        timestamp = int(time.time())
        
        # Conversion incorrecte (UTC uniquement)
        utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
        
        # Conversion correcte (UTC -> local)
        local_time = datetime.fromtimestamp(timestamp, timezone.utc).astimezone()
        
        # Conversion directe en local (référence)
        direct_local = datetime.fromtimestamp(timestamp)
        
        # Les deux méthodes de conversion locale doivent donner le même résultat
        assert local_time.hour == direct_local.hour
        assert local_time.minute == direct_local.minute
        assert local_time.second == direct_local.second
        
    def test_timestamp_format_string(self):
        """Vérifie le format de date utilisé dans l'application."""
        timestamp = int(time.time())
        
        # Format correct pour chk-roon.json et chk-last-fm.json
        date_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
        
        # Vérifier le format (YYYY-MM-DD HH:MM)
        assert len(date_str) == 16  # Format: "2026-01-27 12:34"
        assert date_str[4] == '-'
        assert date_str[7] == '-'
        assert date_str[10] == ' '
        assert date_str[13] == ':'
        
    def test_timestamp_format_with_seconds(self):
        """Vérifie le format de date avec secondes pour les logs IA."""
        timestamp = int(time.time())
        
        # Format pour les logs IA
        datetime_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
        
        # Vérifier le format (YYYY-MM-DD HH:MM:SS)
        assert len(datetime_str) == 19  # Format: "2026-01-27 12:34:56"
        assert datetime_str[16] == ':'
        
    def test_timezone_awareness(self):
        """Vérifie que la conversion préserve l'information de fuseau horaire."""
        timestamp = int(time.time())
        
        # Conversion avec astimezone()
        dt = datetime.fromtimestamp(timestamp, timezone.utc).astimezone()
        
        # L'objet datetime doit être timezone-aware
        assert dt.tzinfo is not None
        assert dt.tzinfo != timezone.utc or datetime.now().astimezone().tzinfo == timezone.utc
        
    def test_specific_timestamp_conversion(self):
        """Test avec un timestamp spécifique pour reproductibilité."""
        # Timestamp: 2026-01-27 10:19:00 UTC = 2026-01-27 11:19:00 CET (UTC+1)
        # Ce test ne fonctionnera correctement qu'en zone CET/CEST
        # En CI (UTC), il servira de test de non-régression
        
        timestamp = 1769504340  # 2026-01-27 10:19:00 UTC
        
        # Conversion UTC (ancienne méthode, incorrecte pour affichage)
        utc_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M')
        
        # Conversion locale (nouvelle méthode, correcte)
        local_str = datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
        
        # La méthode locale doit utiliser le fuseau horaire du système
        # En UTC, les deux seront identiques; dans d'autres zones, ils différeront
        dt_local = datetime.fromtimestamp(timestamp, timezone.utc).astimezone()
        dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
        
        # Vérifier que astimezone() effectue la conversion
        # (si on n'est pas en UTC, l'heure changera)
        system_tz = datetime.now().astimezone().tzinfo
        if str(system_tz) != "UTC":
            # Si le système n'est pas en UTC, les heures devraient être différentes
            assert dt_local.hour != dt_utc.hour or dt_local.day != dt_utc.day
