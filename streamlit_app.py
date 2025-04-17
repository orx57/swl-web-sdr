import streamlit as st
import json
import requests

import constants


# Fonction pour charger les données CSV
def load_csv(url, filters):
    return pd.read_csv(url)


# Fonction pour charger les données JSON
def load_json(url, filters):
    response = requests.get(url)
    return json.loads(response.text)


# Dictionnaire des fonctions de chargement
loading_functions = {
    "csv": load_csv,
    "json": load_json,
}


# Fonction pour charger les données avec mise en cache
def load_data(url, data_type, load=False, filters=None):
    if load:
        try:
            return loading_functions[data_type](url, filters)
        except KeyError:
            raise ValueError(f"Type de données non pris en charge : {data_type}")
    else:
        return None


# Application principale
st.title("📻 SWL Web SDR")

data = {
    name: load_data(
        params["url"], params["data_type"], params.get("load"), params.get("filters")
    )
    for name, params in constants.data_sources.items()
}

with st.sidebar:

    st.warning(
        """
        L'application est en pleine évolution...
        Attendez-vous à de passionnantes nouveautés très prochainement !
        """,
        icon="⚠️",
    )

st.header("Liste des WebSDR publiques actifs")

st.json(data, expanded=False)

# if data:
#     for source, devices in data.items():
#         st.subheader(f"Source: {source}")
#         for device in devices.get("devices", []):
#             st.write(f"**Nom :** {device.get('name', 'Inconnu')}")
#             st.write(f"**URL :** {device.get('url', 'Non spécifiée')}")
#             st.write(f"**Statut :** {device.get('status', 'Non spécifié')}")
#             st.write("---")

st.subheader("A propos de l'application", divider=True)

st.markdown(
    """
    Cette application permet d'afficher les **données publiques des WebSDR
    publiques** à partir de différentes API et sources de données .
    """
)

st.caption(
    """Auteur : F5703SWL - Olivier ([GitHub](https://github.com/orx57)
    & [LinkedIn](https://www.linkedin.com/in/orx57)) · Avril 2025
    """
)
