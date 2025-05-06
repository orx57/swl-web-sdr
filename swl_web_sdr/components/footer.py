import streamlit as st

import config


# Page footer
def footer():

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
            author=config.author, version=config.version
        )
    )
