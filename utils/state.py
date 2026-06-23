"""
CitizenVoice AI - Shared App State

Cached resources (DB connection, loaded ML models, data fetch) shared across
all pages via Streamlit's cache. Importing these same function objects from
every page ensures the cache is reused instead of re-initialized per page.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db import get_connection, init_db, seed_from_csv, fetch_all
from utils.inference import load_models

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "sqlite.db")


@st.cache_resource(show_spinner=False)
def get_db_connection():
    if not os.path.exists(DB_PATH):
        conn = init_db(reset=True)
        seed_from_csv(conn)
    else:
        conn = init_db(reset=False)
    return conn


@st.cache_resource(show_spinner="Loading AI models...")
def get_models():
    return load_models()


@st.cache_data(show_spinner=False, ttl=3)
def get_data():
    conn = get_db_connection()
    return fetch_all(conn)


def refresh_data():
    """Call after inserting new records so the dashboard reflects them immediately."""
    get_data.clear()
