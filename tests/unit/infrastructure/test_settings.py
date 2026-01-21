import pytest
from pathlib import Path
from src.infrastructure.services.settings_service import SettingsService

def test_settings_service_persistence():
    service = SettingsService.instance()
    
    # Test string
    service.set("test_key", "hello")
    assert service.get("test_key") == "hello"
    
    # Test bool
    service.set("test_bool", True)
    assert service.get_bool("test_bool") is True
    
    # Test float
    service.set("test_float", 1.5)
    assert service.get_float("test_float") == 1.5
    
    # Test int
    service.set("test_int", 42)
    assert service.get_int("test_int") == 42
