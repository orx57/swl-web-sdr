from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

import config


# Page sidebar
def sidebar(user_locale):

    # Get time and user timezone
    tz = st.context.timezone or config.DEFAULT_TIMEZONE
    tz_obj = ZoneInfo(tz)
    now = datetime.now(timezone.utc)

    with st.sidebar:
        # Language selector with pre-translated label
        lang_label = _("🌍 Language")
        selected_lang = st.selectbox(
            lang_label,
            options=list(config.LANGUAGES.keys()),
            format_func=lambda x: config.LANGUAGES[x],
            index=list(config.LANGUAGES.keys()).index(st.session_state.language),
            key="lang_selector",
        )

        # Update translation and reload if language changes
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()

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
