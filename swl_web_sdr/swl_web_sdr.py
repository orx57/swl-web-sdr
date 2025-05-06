import streamlit as st

from .components import *
from .pages import *


def swl_web_sdr(user_locale, devices):

    # Set the page configuration
    st.set_page_config(
        initial_sidebar_state="expanded",
        layout="wide",
        page_icon="📻",
        page_title="SWL Web SDR",
    )

    # Sidebar
    sidebar(user_locale)

    # Content
    index(devices)

    # Footer
    footer()
