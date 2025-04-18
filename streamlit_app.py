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
    return json.loads(response.text)


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


# Dictionary of loading functions
loading_functions = {
    "csv": load_csv,
    "json": load_json,
}

#
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

# Retrieve the user's browser language
user_locale = st.context.locale  # For example, "fr-FR" or "en-US"

# Extract the primary language (e.g., "fr" or "en")
lang = user_locale.split("-")[0]  # Take the first part before the hyphen

# Translation setup
_ = setup_i18n(lang)  # _ is the convention for the translation function

# Main application

# Set the page configuration
st.set_page_config(layout="wide")

# Sidebar
with st.sidebar:

    st.info(
        _(
            """The application is evolving...
        Expect exciting new features very soon!
        """
        ),
        icon="ℹ️",
    )

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

st.json(data, expanded=False)

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
