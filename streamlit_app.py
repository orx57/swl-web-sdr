import gettext
import json
from datetime import datetime, timezone

import pytz
import requests
import streamlit as st

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
            all_devices.extend(devices)
    return all_devices


# Dictionary of loading functions
loading_functions = {
    "csv": load_csv,
    "json": load_json,
}

# Retrieve the user's browser language
user_locale = st.context.locale  # For example, "fr-FR" or "en-US"

# Extract the primary language (e.g., "fr" or "en")
lang = user_locale.split("-")[0]  # Take the first part before the hyphen

# Translation setup
_ = setup_i18n(lang)  # _ is the convention for the translation function

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

    # Author information message
    st.info(
        _(
            """The application is evolving...
        Expect exciting new features very soon!
        """
        ),
        icon="ℹ️",
    )

    # User context information
    st.caption(
        _(
            """Language: {lang}  
        Locale: {user_locale}  
        Time: {now_local}  
        Timezone: {tz}  
        UTC time: {now_utc}
        """
        ).format(
            lang=lang,
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
        "gps": _("GPS"),
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
