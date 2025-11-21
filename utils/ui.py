import streamlit as st
import os

def load_css(css_file_path):
    """
    Load CSS from a file and inject it into the Streamlit app.
    
    Args:
        css_file_path (str): Relative path to the CSS file.
    """
    try:
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load CSS file: {e}")
