"""Native corner-menu actions and session-only survey upload dialog."""

from pathlib import Path

import streamlit as st

from src.market_data import export_survey_csv
from src.shared_data import manage_data_dialog


def render_menu_actions(frame=None, synthetic=True, upload_action=None, export_data=None, export_name=None):
    """Hidden native widgets are invoked by the two visible corner-menu items."""
    with st.container(key="menu_actions"):
        st.download_button("Export opportunity ranking CSV" if export_name else "Export filtered survey CSV",data=export_data if export_data is not None else export_survey_csv(frame) if frame is not None else b"",
            file_name=export_name or "market_intelligence_export.csv",
            mime="text/csv",on_click="ignore",key="export_survey",disabled=frame is None and export_data is None)
        if st.button("Upload CSV",key="menu_upload"):
            (upload_action or manage_data_dialog)()
    script = (Path(__file__).resolve().parents[1] / "assets/native_menu.js").read_text(encoding="utf-8")
    st.html("<script>" + script + "</script>",unsafe_allow_javascript=True)
