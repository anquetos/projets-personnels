# ------- Import modules and librairies --------

from utils import * # functions from 'utils.py'
from meteo_france import Client # functions from 'meteo_france.py'
# import folium
import streamlit as st
# from streamlit_folium import st_folium
# import requests
from datetime import datetime, timedelta
import pandas as pd
from io import StringIO

# ------- Import data ------

# Import and clean weather stations from csv
df_stations = pd.read_csv('./datasets/weather-stations-list.csv', sep=';')

def clean_stations_df(df):
    df.columns = df.columns.str.lower()
    df['nom_usuel'] = df['nom_usuel'].str.title()
    df = df.drop(columns=['id_omm', 'pack'])

clean_stations_df(df_stations)

# ------- Initialize session_state ------

keys = ['search_input', 'selected', 'id_station', 'current_time_utc']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ''

# ------- Main code of app : page config ------

st.set_page_config(
    page_title='Météo App',
    page_icon='⛅',
    initial_sidebar_state='expanded'
)

st.title('Météo app')

# ------- Main code of app : sidebar ------

with st.sidebar:

    st.markdown('## Recherche')

    st.text_input(
        label=':point_right: 1. Chercher une commune',
        placeholder='Tapez votre recherche...',
        value='',
        key='search_input'
    )

    def reset_click():
        st.session_state['search_input'] = ''
        st.session_state['selected'] = ''

    st.button('Effacer', on_click=reset_click)

    st.selectbox(
        label=':point_right: 2. Faites votre choix',
        options=search_municipality(st.session_state['search_input']),
        index=None,
        format_func=lambda x: f'{x['label']} ({x['context'].split(',')[0]})',
        key='selected',
        placeholder='Sélectionnez un résultat...'
        )
    
    'st_session_state object :', st.session_state

# ------- Main code of app : page ------
    
if st.session_state['selected']:

    with st.spinner('Chargement des données en cours...'):
    
        st.markdown('### 🗼 Station')

        # Wrap below section in function to cache data and prevent 'rerun' if
        # selected station doesn't change
        @st.cache_data
        def get_display_station_info(station):

            # Get the list of nearest observation stations
            nearest_stations_list = find_nearest_stations(
                df_stations, station['coordinates'])
            
            # Get the 'city' and 'context' of the nearest station
            nearest_station_address = reverse_geocoding(
                [
                    nearest_stations_list[0]['latitude'],
                    nearest_stations_list[0]['longitude']
                ]
            )

            with st.expander(
                f'{nearest_stations_list[0]['nom_usuel']} '
                f'({nearest_station_address['city']}, '
                f'{nearest_station_address['context']})'
            ):

                # Build and display information text about the nearest station
                nearest_station_text = f'''
                    * id : {nearest_stations_list[0]['id_station']}
                    * Altitude : {nearest_stations_list[0]['altitude']} m
                    * Distance de {st.session_state['selected']['label']} : 
                    {nearest_stations_list[0]['distance']:.1f} km
                    * Date d'ouverture : {nearest_stations_list[0]['date_ouverture']}
                '''
                st.markdown(nearest_station_text)

            # Save id of selected station in 'session_state'
            st.session_state['id_station'] = nearest_stations_list[0]['id_station']
            
        get_display_station_info(st.session_state['selected'])

        st.markdown('### 🔎 Observations')

        st.markdown('##### En temps réel')

        # Wrap below section in function to cache data and prevent 'rerun' if 
        # station_id doesn't change
        @st.cache_data
        def get_display_current_data(id_station):

            # Get current weather informations from the nearest station
            current_obs = Client().get_observation(
                id_station, '')
            
            # Calculate utc time of the previous weather information
            previous_time = (
                datetime.strptime(
                    current_obs['validity_time_utc'], '%Y-%m-%dT%H:%M:%SZ')
                - timedelta(hours=1)
            )

            # Get previous weather informations from the nearest station
            previous_obs = Client().get_observation(
                id_station,
                previous_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )

            # Function to calculate 'delta' for st.metric
            def delta(x, y):
                if x == y:
                    delta = None
                elif x and y is not None:
                    delta = x - y
                else:
                    delta = None

                return delta

            with st.container(border=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    d = delta(current_obs['t'], previous_obs['t'])
                    c = current_obs['t']
                    st.metric(
                        label='Température',
                        value=(f'{c} °C') if c is not None else None,
                        delta=(f'{d:.1f} °C') if d is not None else None
                    )
                with col2:
                    d = delta(current_obs['u'], previous_obs['u'])
                    c = current_obs['u']
                    st.metric(
                        label='Humidité',
                        value=(f'{c} %') if c is not None else None,
                        delta=(f'{round(d)} %') if d is not None else None
                    )
                with col3:
                    d = delta(current_obs['ff'], previous_obs['ff'])
                    c = current_obs['ff']
                    st.metric(
                        label='Vent',
                        value=(f'{c} km/h') if c is not None else None,
                        delta=(f'{round(d)} km/h') if d is not None else None
                    )
                with col4:
                    d = delta(current_obs['rr1'], previous_obs['rr1'])
                    c = current_obs['rr1']
                    st.metric(
                        label='Précipitations 1h',
                        value=(f'{c} mm') if c is not None else None,
                        delta=(f'{round(d)} mm') if d is not None else None
                    )

                # st.divider()

                col5, col6, col7, col8 = st.columns(4)
                with col5:
                    d = delta(current_obs['vv'], previous_obs['vv'])
                    c = current_obs['vv']
                    st.metric(
                        label='Visibilité',
                        value=(f'{c} m') if c is not None else None,
                        delta=(f'{round(d)} m') if d is not None else None
                    )
                with col6:
                    d = delta(current_obs['sss'], previous_obs['sss'])
                    c = current_obs['sss']
                    st.metric(
                        label='Neige',
                        value=(f'{c} m') if c is not None else None,
                        delta=(f'{round(d)} m') if d is not None else None
                    )
                with col7:
                    d = delta(current_obs['insolh'], previous_obs['insolh'])
                    c = current_obs['insolh']
                    st.metric(
                        label='Ensoleillement',
                        value=(f'{c} min') if c is not None else None,
                        delta=(f'{round(d)} min') if d is not None else None
                    )
                with col8:
                    d = delta(current_obs['pres'], previous_obs['pres'])
                    c = current_obs['pres']
                    st.metric(
                        label='Pression',
                        value=(f'{c} hPa') if c is not None else None,
                        delta=(f'{round(d)} hPa') if d is not None else None
                    )

                st.caption(f'Mise à jour : {current_obs['validity_time']}')

            # Save current UTC time in 'session_state'
            st.session_state['current_time_utc'] = current_obs['validity_time_utc']

        get_display_current_data(st.session_state['id_station'])

        st.markdown('##### Le temps d\'avant')

        n_year = st.number_input(
            label='De combien d\'année(s) souhaitez-vous remonter en arrière ?',
            min_value=1,
            max_value=50,
        )

        # Calculate utc time of the past weather information
        past_time = (
            datetime.strptime(
                st.session_state['current_time_utc'], '%Y-%m-%dT%H:%M:%SZ')
        )
        past_time = past_time.replace(year=past_time.year-n_year)

        # Get previous weather informations from the nearest station
        past_obs_order = Client().order_hourly_weather_info(
            st.session_state['id_station'],
            past_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            past_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        past_obs = Client().get_order_data(past_obs_order)

        df_past_obs = pd.read_csv(StringIO(past_obs), sep=';')

        st.write(df_past_obs)

else:

    st.info('''
        ### :point_left: Aucune commune n'est sélectionnée !
        Pour afficher les informations et les relevés d\'une station 
        d\'observation, commencez par **sélectionner une commune**. 
            
        Pour cela, utilisez la **zone de recherche** située dans le **menu 
        latéral** puis **faites votre choix** parmi les **résultats proposés**.
    ''')



# ------- WIP ------
        
# m = folium.Map(location=[46.71109, 1.7191036], zoom_start=6)

# # call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)