"""
Constants module for SWL Web SDR application
This module contains all constants needed for the application,
including API URLs, data sources and localization settings.
"""

# Application information
author = "F5703SWL - Olivier"  # Application author
version = "2025.17.1"  # Format: YYYY.ww.D (Year.Week.WeekDay)

# API URLs
# KiwiSDR Public Device List (Refreshed every 15 minutes)
KIWISDR_JSON_URL = "https://www.rx-888.com/api/devices"

# Web-888 Public Device List (Refreshed every 15 minutes)
WEB888_JSON_URL = "https://www.rx-888.com/api/devices"

# Data sources configuration
# Each source contains:
# - data_type: type of data (json, csv)
# - load: boolean indicating if source should be loaded at startup
# - name: display name for the source
# - url: API endpoint URL
data_sources = {
    "kiwisdr": {
        "data_type": "json",
        "load": False,
        "name": "KiwiSDR",
        "url": KIWISDR_JSON_URL,
    },
    "web888": {
        "data_type": "json",
        "load": True,
        "name": "Web-888",
        "url": WEB888_JSON_URL,
    },
}

# Internationalization settings
# Available languages in the application
LANGUAGES = {"fr": "Français", "en": "English"}

# Default localization settings
DEFAULT_LOCALE = "en-US"  # Default locale if not detected
DEFAULT_TIMEZONE = "UTC"  # Default timezone if not detected
