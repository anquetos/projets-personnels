# Import functions from 'utils.py'
from utils import *

# Import libraries
import streamlit as st
from streamlit_searchbox import st_searchbox
# import requests
# import pandas as pd
# import io
# from geopy.distance import geodesic

# Main code of app
# ----------------

# Create a searchbox component for municipality
selected_municipality = st_searchbox(
    search_function=lambda query: search_municipality(query),
    placeholder='Tapez votre recherche...',
    label='Chercher une commune dans la Base Adresse Nationale'
)