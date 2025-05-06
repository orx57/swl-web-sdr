import streamlit as st

from ..backend import *

# Page index
def index(devices):

    # Page content
    st.title(_("📻 SWL Web SDR"))

    st.header(_("List of Active Public WebSDRs"))

    # Display metrics for the number of SDRs and users
    active_sdr, active_user, total_sdr, lucky_button = st.columns([1, 1, 1, 1])

    # Get all devices
    combined_devices = aggregate_devices(devices)

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

    # Bouton QSL Surprise dans la dernière colonne
    with lucky_button:
        if st.button(
            _("🎲 Random QSL !"),
            help=_("Discover a random WebSDR"),
            use_container_width=True,
        ):
            lucky_sdr = get_random_available_sdr(active_devices)
            if lucky_sdr:
                js = f"""<script>
                    window.open('{lucky_sdr["url"]}', '_blank');
                </script>"""
                st.components.v1.html(js, height=0)
            else:
                st.warning(_("No WebSDR available at the moment"))

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
            "users_ratio": st.column_config.ProgressColumn(
                _("Occupation"),
                help=_("WebSDR occupation rate"),
                format="%.0f%%",
                min_value=0,
                max_value=100,
            ),
            "max_users": st.column_config.NumberColumn(
                _("Max Users"),
                help=_("Maximum number of users"),
            ),
            "antenna": _("Antenna"),
            "status": None,
            "bands": st.column_config.TextColumn(
                _("Bands"),
                help=_("Frequency range in MHz"),
            ),
            "grid": st.column_config.TextColumn(
                _("Grid"),
                help=_("Maidenhead Grid Locator"),
            ),
            "country_code": st.column_config.TextColumn(
                _("Country Code"),
                help=_("Country code (ISO)"),
            ),
            "city": st.column_config.TextColumn(
                _("City"),
                help=_("City name"),
            ),
            "region": st.column_config.TextColumn(
                _("Region"),
                help=_("State/Region/Province"),
            ),
            "gps": st.column_config.TextColumn(
                _("GPS"),
                help=_("GPS coordinates"),
            ),
        },
        column_order=(
            # Informations principales
            "name",
            "url",
            "source",
            # Statistiques d'utilisation
            "users",
            "users_ratio",
            "max_users",
            # Informations techniques
            "antenna",
            "bands",
            "snr",
            "uptime",
            # Localisation
            "country_code",
            "city",
            "region",
            "grid",
            "gps",
            # Champ caché
            "status",
        ),
        hide_index=True,
    )
