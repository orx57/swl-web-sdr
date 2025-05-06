import gettext

import streamlit as st

import config
from swl_web_sdr import *


# Configuration for gettext
def setup_i18n(lang):
    localedir = "assets/locales"  # Folder containing translations
    translation = gettext.translation(
        "messages", localedir, languages=[lang], fallback=True
    )
    translation.install()
    return translation.gettext


# Retrieve the user's browser language with fallback
user_locale = st.context.locale or config.DEFAULT_LOCALE

# Get initial language from locale
initial_lang = user_locale.split("-")[0]
if initial_lang not in config.LANGUAGES:
    initial_lang = config.DEFAULT_LOCALE

# Create session state for language if it doesn't exist
if "language" not in st.session_state:
    st.session_state.language = initial_lang

# Initialize translation with current language
_ = setup_i18n(st.session_state.language)

# Load the data sources from constants
devices = {
    name: load_data(
        params["url"], params["data_type"], params.get("load"), params.get("filters")
    )
    for name, params in config.data_sources.items()
}

# Main application
swl_web_sdr(user_locale, devices)
