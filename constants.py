"""Constantes nécessaires à l'application"""

# Web-888 Public Device List (Refresh every 15 minutes)
WEB888_JSON_URL = (
    "https://www.rx-888.com/api/devices"
)

# Dictionnaire associant les URL à leurs types de données et à leurs filtres
data_sources = {
    "web888": {
        "data_type": "json",
        "load": True,
        "url": WEB888_JSON_URL,
    },
}
