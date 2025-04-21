import gettext
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import reverse_geocoder as rg
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
        # If it's a string, try different formats
        if isinstance(gps_data, str):
            # Clean the string from parentheses and spaces
            clean_coords = gps_data.strip("() ").replace(" ", "")
            # Format "(lat, lon)" or "lat,lon"
            lat, lon = map(float, clean_coords.split(","))
        # If it's already a dict/list with lat/lon
        elif isinstance(gps_data, (dict, list)):
            if isinstance(gps_data, dict):
                lat = float(gps_data.get("lat", gps_data.get("latitude")))
                lon = float(gps_data.get("lon", gps_data.get("longitude")))
            else:
                lat, lon = map(float, gps_data[:2])

        # Get Maidenhead code
        grid_code = maidenhead.toMaiden(lat, lon, 3)
        return grid_code

    except Exception:
        return None


@st.cache_data(persist=True, show_spinner="Chargement des données de géocodage...")
def get_country_from_gps(gps_data):
    """Get country from GPS coordinates using reverse_geocoder with Streamlit persistent cache"""
    if not gps_data:
        return None
    try:
        # Parse coordinates
        if isinstance(gps_data, str):
            clean_coords = gps_data.strip("() ").replace(" ", "")
            lat, lon = map(float, clean_coords.split(","))
        elif isinstance(gps_data, (dict, list)):
            if isinstance(gps_data, dict):
                lat = float(gps_data.get("lat", gps_data.get("latitude")))
                lon = float(gps_data.get("lon", gps_data.get("longitude")))
            else:
                lat, lon = map(float, gps_data[:2])

        # Utilise reverse_geocoder avec les coordonnées arrondies
        result = rg.search((round(lat, 4), round(lon, 4)))
        if result and len(result) > 0:
            return result[0].get("cc", "").upper()

    except Exception as e:
        st.error(f"Erreur de géocodage: {str(e)}")
        return None

    return None


def format_gps(gps_str):
    """Format GPS coordinates in a human readable format: 48.8567°N, 2.3508°E"""
    if not gps_str:
        return None
    try:
        # Clean the string from parentheses and spaces
        clean_coords = gps_str.strip("() ").replace(" ", "")
        lat, lon = map(float, clean_coords.split(","))

        # Determine directions
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"

        # Format with 4 decimals and directions
        return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    except Exception:
        return gps_str


# Generic aggregation of data from all sources
def aggregate_devices(data_sources):
    all_devices = []
    for source_name, source_data in data_sources.items():
        if source_data and "devices" in source_data:
            # Deduplicate devices from this source
            devices = deduplicate_devices(source_data["devices"])
            # Use the name defined in constants.py instead of the key
            source_display_name = constants.data_sources[source_name]["name"]
            for device in devices:
                device["source"] = source_display_name
                # Calculate grid locator and country before formatting GPS
                device["grid"] = get_grid_locator(device.get("gps"))
                device["country"] = get_country_from_gps(device.get("gps"))
                # Format GPS coordinates after
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
tz = st.context.timezone or constants.DEFAULT_TIMEZONE
tz_obj = ZoneInfo(tz)
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
        index=(
            list(constants.LANGUAGES.keys()).index(initial_lang)
            if initial_lang in constants.LANGUAGES
            else 0
        ),
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
            user_locale=user_locale,
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

# Get all devices
combined_devices = aggregate_devices(data)

# Filter active devices
active_devices = [
    device for device in combined_devices if device.get("status") == "active"
]

# Calculate metrics only for active devices
total_active = len(active_devices)
total_users = sum(int(device.get("users", 0)) for device in active_devices)
total_sdrs = len(combined_devices)  # Keep total of all devices

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
        "grid": st.column_config.TextColumn(
            _("Grid"),
            help=_("Maidenhead Grid Locator"),
        ),
        "country": st.column_config.TextColumn(
            _("Country"),
            help=_("Country code"),
        ),
        "gps": st.column_config.TextColumn(
            _("GPS"),
            help=_("GPS coordinates"),
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
        "country",
        "grid",
        "gps",
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
