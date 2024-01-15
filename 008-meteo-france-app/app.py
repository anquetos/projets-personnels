# ------- Import modules and librairies --------

from utils import * # functions from 'utils.py'
from meteo_france import Client # functions from 'meteo_france.py'
# import folium
import streamlit as st
# from streamlit_folium import st_folium
# import requests
import pandas as pd

# ------- Import data ------

# Import and clean weather stations from csv
df_stations = pd.read_csv('./datasets/weather-stations-list.csv', sep=';')

def clean_stations_df(df):
    df.columns = df.columns.str.lower()
    df['nom_usuel'] = df['nom_usuel'].str.title()
    df = df.drop(columns=['id_omm', 'pack'])

clean_stations_df(df_stations)

# ------- Main code of app : sidebar ------

with st.sidebar:

    st.markdown('## Commune')

    st.text_input(
        label='Quelle commune cherchez-vous ?',
        placeholder='Tapez votre recherche...',
        value='',
        key='search_input'
    )

    def reset_click():
        st.session_state['search_input'] = ''
        st.session_state['selected'] = None

    st.button('Effacer', on_click=reset_click)

    st.selectbox(
        label='Choisissez une commune',
        options=search_municipality(st.session_state['search_input']),
        index=None,
        format_func=lambda x: f'{x['label']} ({x['context'].split(',')[0]})',
        key='selected',
        placeholder='Sélectionnez un résultat...'
        )
    
    'st_session_state object :', st.session_state

# ------- Main code of app : page ------
    
st.title('Météo France app')

st.markdown('## Informations météorologiques')

with st.spinner('Chargement des données en cours...'):

    if st.session_state['selected']:

        # Get the list of nearest observation stations
        nearest_stations_list = find_nearest_stations(
            df_stations,st.session_state['selected']['coordinates'])

        # Get the 'city' and 'context' of the nearest station
        nearest_station_address = reverse_geocoding(
            [
                nearest_stations_list[0]['latitude'],
                nearest_stations_list[0]['longitude']
            ]
        )

        # Get and display last weather informations from the nearest station
        current_obs = Client().get_observation(
            nearest_stations_list[0]['id_station'], '')
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(label='Température (°C)',
                        value=(current_obs['t'] if not None else '--'))
            with col2:
                st.metric(label='Humidité (%)',
                        value=(current_obs['u'] if not None else '--'))
            with col3:
                st.metric(label='Précipitations (mm)',
                        value=(current_obs['rr1'] if not None else '--'))
            with col4:
                st.metric(label='Vent (km/h)',
                          value=(current_obs['ff'] if not None else '--'))
            with col5:
                st.metric(label='Soleil (min)',
                        value=(current_obs['insolh'] if not None else '--'))
            st.caption(f'Dernière mise à jour des données : '
                       f'{current_obs['validity_time']}')
            
        # Build and display information text about the nearest station
        nearest_station_text = f'''
            Les données proviennent de la station d'observation 
            *{nearest_stations_list[0]['nom_usuel']} 
            (id : {nearest_stations_list[0]['id_station']})* située à 
            *{nearest_station_address['city']}, 
            {nearest_station_address['context']} ({nearest_stations_list[0]['distance']:.1f} 
            km* de la commune sélectionnée).
        '''
        st.markdown(nearest_station_text)

    else:
        st.warning(
            f'Vous devez sélectionner une commune pour pouvoir afficher les '
            f'informations de la station météorologique la plus proche.'
        )



# ------- WIP ------
        
# m = folium.Map(location=[46.71109, 1.7191036], zoom_start=6)

# # call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)