import gettext
import json
from datetime import datetime, timezone

import pytz
import requests
import streamlit as st
from vgrid.utils import maidenhead

import constants


# Function to load CSV data
def load_csv(url, filters):
    return pd.read_csv(url)


# Function to load JSON data
def load_json(url, filters):
    response = requests.get(url)
    data = json.loads(response.text)

    # Reformat SNR values
    if "devices" in data:
        for device in data["devices"]:
            if "snr" in device:
                # Replace the comma by dot in SNR value
                device["snr"] = float(device["snr"].replace(",", "."))

    return data


# Function to load data with caching
def load_data(url, data_type, load=False, filters=None):
    if load:
        try:
            return loading_functions[data_type](url, filters)
        except KeyError:
            raise ValueError(f"Unsupported data type: {data_type}")
    else:
        return None


# Configuration for gettext
def setup_i18n(lang):
    localedir = "locales"  # Folder containing translations
    translation = gettext.translation(
        "messages", localedir, languages=[lang], fallback=True
    )
    translation.install()
    return translation.gettext


# Function to deduplicate devices
def deduplicate_devices(devices):
    """Remove duplicate devices based on URL"""
    unique_devices = {}
    for device in devices:
        url = device.get("url")
        if url:
            # Keep only the first occurrence or update if better status
            if url not in unique_devices or (
                device.get("status") == "active"
                and unique_devices[url].get("status") != "active"
            ):
                unique_devices[url] = device
    return list(unique_devices.values())


def get_grid_locator(gps_data):
    """Convert GPS coordinates to Maidenhead Grid Locator and get grid center"""
    if not gps_data:
        return None
    try:
        # Si c'est une string, on essaie plusieurs formats
        if isinstance(gps_data, str):
            # Nettoyer la chaîne des parenthèses et espaces
            clean_coords = gps_data.strip("() ").replace(" ", "")
            # Format "(lat, lon)" ou "lat,lon"
            lat, lon = map(float, clean_coords.split(","))
        # Si c'est déjà un dict/list avec lat/lon
        elif isinstance(gps_data, (dict, list)):
            if isinstance(gps_data, dict):
                lat = float(gps_data.get("lat", gps_data.get("latitude")))
                lon = float(gps_data.get("lon", gps_data.get("longitude")))
            else:
                lat, lon = map(float, gps_data[:2])

        # Obtenir le code Maidenhead et les coordonnées du centre
        grid_code = maidenhead.toMaiden(lat, lon, 3)
        grid_center = maidenhead.maidenGrid(grid_code)
        return grid_code

    except Exception:
        return None


def format_gps(gps_str):
    """Format GPS coordinates in a human readable format: 48.8567°N, 2.3508°E"""
    if not gps_str:
        return None
    try:
        # Nettoyer la chaîne des parenthèses et espaces
        clean_coords = gps_str.strip("() ").replace(" ", "")
        lat, lon = map(float, clean_coords.split(","))

        # Déterminer les directions
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"

        # Formater avec 4 décimales et les directions
        return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    except Exception:
        return gps_str


# Agrégation générique des données de toutes les sources
def aggregate_devices(data_sources):
    all_devices = []
    for source_name, source_data in data_sources.items():
        if source_data and "devices" in source_data:
            # Dédupliquer les appareils de cette source
            devices = deduplicate_devices(source_data["devices"])
            # Utiliser le nom défini dans constants.py plutôt que la clé
            source_display_name = constants.data_sources[source_name]["name"]
            for device in devices:
                device["source"] = source_display_name
                # Calculer le grid locator avant de formater les GPS
                device["grid"] = get_grid_locator(device.get("gps"))
                # Formater les coordonnées GPS après
                if device.get("gps"):
                    device["gps"] = format_gps(device["gps"])
            all_devices.extend(devices)
    return all_devices


# Dictionary of loading functions
loading_functions = {
    "csv": load_csv,
    "json": load_json,
}

# Retrieve the user's browser language with fallback
user_locale = st.context.locale or constants.DEFAULT_LOCALE

# Get initial language from locale
initial_lang = user_locale.split("-")[0]

# Get time and user timezone
tz = st.context.timezone
tz_obj = pytz.timezone(tz)
now = datetime.now(timezone.utc)

# Load the data sources from constants
data = {
    name: load_data(
        params["url"], params["data_type"], params.get("load"), params.get("filters")
    )
    for name, params in constants.data_sources.items()
}

# Main application

# Set the page configuration
st.set_page_config(layout="wide")

# Sidebar
with st.sidebar:
    # Language selector
    selected_lang = st.selectbox(
        "🌍 Language / Langue",
        options=list(constants.LANGUAGES.keys()),
        format_func=lambda x: constants.LANGUAGES[x],
        index=list(constants.LANGUAGES.keys()).index(initial_lang) if initial_lang in constants.LANGUAGES else 0
    )
    
    # Translation setup with selected language
    _ = setup_i18n(selected_lang)
    
    # Info message and other sidebar content
    st.info(
        _(
            """The application is evolving...
        Expect exciting new features very soon!
        """
        ),
        icon="ℹ️",
    )
    
    # Update user context information with selected language
    st.caption(
        _(
            """Language: {lang}  
        Locale: {user_locale}  
        Time: {now_local}  
        Timezone: {tz}  
        UTC time: {now_utc}
        """
        ).format(
            lang=selected_lang,
            user_locale=user_locale,  # Affichage direct de la locale utilisateur
            now_local=now.astimezone(tz_obj),
            tz=tz,
            now_utc=now,
        )
    )

# Page content
st.title(_("📻 SWL Web SDR"))

st.header(_("List of Active Public WebSDRs"))

# st.json(data, expanded=False)

# Display metrics for the number of SDRs and users
active_sdr, active_user, total_sdr = st.columns(3)

# Obtenir tous les appareils
combined_devices = aggregate_devices(data)

# Filtrer les appareils actifs
active_devices = [
    device for device in combined_devices if device.get("status") == "active"
]

# Calcul des métriques sur les appareils actifs uniquement
total_active = len(active_devices)
total_users = sum(int(device.get("users", 0)) for device in active_devices)
total_sdrs = len(combined_devices)  # Garde le total de tous les appareils

active_sdr.metric(
    _("Active SDRs"),
    total_active,
    border=True,
)
active_user.metric(
    _("Active Users"),
    total_users,
    border=True,
)
total_sdr.metric(_("Total SDRs"), total_sdrs, border=True)

# Display the list of SDRs
st.dataframe(
    active_devices,
    column_config={
        "url": st.column_config.LinkColumn(
            _("URL"),
            display_text=r".*://(.*:\d+)",
        ),
        "uptime": st.column_config.NumberColumn(
            _("Uptime"),
            help=_("Uptime in seconds"),
        ),
        "name": _("Name"),
        "source": st.column_config.TextColumn(
            _("Source"),
            help=_("Data source origin"),
        ),
        "snr": st.column_config.NumberColumn(
            _("SNR"),
            help=_("Signal-to-Noise Ratio"),
            format="%.2f",
        ),
        "users": st.column_config.NumberColumn(
            _("Users"),
            help=_("Number of active users"),
        ),
        "max_users": st.column_config.NumberColumn(
            _("Max Users"),
            help=_("Number of maximum users"),
        ),
        "antenna": _("Antenna"),
        "status": None,
        "bands": _("Bands"),
        "gps": st.column_config.TextColumn(
            _("GPS"),
            help=_("GPS coordinates"),
        ),
        "grid": st.column_config.TextColumn(
            _("Grid"),
            help=_("Maidenhead Grid Locator"),
        ),
    },
    column_order=(
        "url",
        "name",
        "antenna",
        "source",
        "snr",
        "users",
        "max_users",
        "uptime",
        "status",
        "bands",
        "gps",
        "grid",
    ),
    hide_index=True,
)

# Page footer
st.subheader(_("About the Application"), divider=True)

st.markdown(
    _(
        """This application displays **public data from active WebSDRs**
    using different APIs and data sources.
    """
    )
)

st.caption(
    _("Author: {author} · Version: {version}").format(
        author=constants.author, version=constants.version
    )
)
