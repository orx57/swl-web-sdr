"""Constants required for application"""

author = "F5703SWL - Olivier"
version = "2025.16.5"

# Web-888 Public Device List (Refresh every 15 minutes)
WEB888_JSON_URL = (
    "https://www.rx-888.com/api/devices"
)

# Dictionary associating URLs with their data types and filters
data_sources = {
    "web888": {
        "data_type": "json",
        "load": True,
        "url": WEB888_JSON_URL,
    },
}
