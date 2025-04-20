"""Constants required for application"""

author = "F5703SWL - Olivier"
version = "2025.16.7"

# KiwiSDR Public Device List (Refresh every 15 minutes)
KIWISDR_JSON_URL = (
    "https://www.rx-888.com/api/devices"
)

# Web-888 Public Device List (Refresh every 15 minutes)
WEB888_JSON_URL = (
    "https://www.rx-888.com/api/devices"
)

# Dictionary associating URLs with their data types and filters
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
