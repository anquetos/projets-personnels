# ------- Import modules and librairies --------

from utils import * # functions from 'utils.py'
from meteo_france import Client # functions from 'meteo_france.py'
# import folium
import streamlit as st
# from streamlit_folium import st_folium
# import requests
from datetime import datetime, timedelta, date, time
import pandas as pd
import numpy as np
from io import StringIO
import plotly.express as px

# ------- Data and variables------

# Import and clean weather stations from csv
df_stations = pd.read_csv('./datasets/weather-stations-list.csv', sep=';',
                          dtype={'Id_station': object}, parse_dates=['Date_ouverture'])

df_stations.columns = df_stations.columns.str.lower()
df_stations['nom_usuel'] = df_stations['nom_usuel'].str.title()

# Create a dictionnay of variables available for plotting
viz_options_dict = {
    't': {'label': 'Température', 'variables': ['tm', 'tmnx', 'tn', 'tx'],
          'unit': '°C', 'graph_type': 'line'},
    'u': {'label': 'Humidité', 'variables': ['um', 'un', 'ux'], 'unit': '%',
          'graph_type': 'line'},
    'ff': {'label': 'Vent', 'variables': ['ffm', 'fxi', 'fxy'], 'unit': 'km/h',
           'graph_type': 'line'},
    'rr': {'label': 'Précipitations', 'variables': ['rr'], 'unit': 'mm',
           'graph_type': 'bar'},
    'sss': {'label': 'Neige', 'variables': ['neigetotx'], 'unit': 'cm',
                'graph_type': 'bar'},
    'inst': {'label': 'Ensoleillement', 'variables': ['inst'], 'unit': 'min',
             'graph_type': 'bar'}
}

# ------- Function for sidebar ------

@st.cache_data # prevent 'rerun' if selected station doesn't change
def get_display_station_info(selected):
    '''
    Searches for the nearest observation station from the selected city then 
    gets and display its information in 'st.expander()'
    Parameters :
    - selected : dictionnary with information on selected city.
    Returns the id of the station and the opening date.
    '''
    # Get the list of nearest observation stations
    nearest_stations_list = find_nearest_stations(
        df_stations, selected['coordinates'])
    
    # Get the 'city' and 'context' of the nearest station
    nearest_station_address = reverse_geocoding(
        [
            nearest_stations_list[0]['latitude'],
            nearest_stations_list[0]['longitude']
        ]
    )

    # Build and display information text about the nearest station
    with st.expander(
        f'{nearest_stations_list[0]['nom_usuel']}'
        f'({nearest_station_address['city']}, '
        f'{nearest_station_address['context']})'
    ):

        nearest_station_text = f'''
            * id : {nearest_stations_list[0]['id_station']}
            * Altitude : {nearest_stations_list[0]['altitude']} m
            * Distance de {st.session_state['selected']['label']} : 
            {nearest_stations_list[0]['distance']:.1f} km
            * Date d'ouverture : {nearest_stations_list[0]['date_ouverture']}
        '''
        st.markdown(nearest_station_text)
        
    return (nearest_stations_list[0]['id_station'],
            nearest_stations_list[0]['date_ouverture'])

# ------- Function for 'current observation' section in main page ------

@st.cache_data # prevent 'rerun' if selected station doesn't change
def get_current_data(id_station):
    '''
    Get observation data of a specific station id for the current hour and the
    hour before.
    Parameters :
    - id_station : id of the station.
    Returns a dictionnary with the data
    '''
    # Get current weather informations from the nearest station
    current_obs = Client().get_observation(id_station, '')

    # Calculate UTC time of the previous weather information
    previous_time = (
        datetime.strptime(current_obs['validity_time_utc'], '%Y-%m-%dT%H:%M:%SZ')
        - timedelta(hours=1)
    )

    # Get previous weather informations from the nearest station
    previous_obs = Client().get_observation(
        id_station, previous_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    # Convert UTC time to local
    current_obs['validity_time'] = datetime_tz_convert(
        current_obs['validity_time_utc'], 'utc_to_local')
    previous_obs['validity_time'] = datetime_tz_convert(
        previous_obs['validity_time_utc'], 'utc_to_local')

    data = {
        'current_obs': current_obs,
        'previous_obs': previous_obs
    }

    return data

# ------- Functions for 'past observation' section in main page ------

def tm_input_parameters():
    '''
    Calculate parameters for 'st.input_date' and 'st.input_time' for the
    Time Machine section.
    Returns a tuple with the parameters.
    '''
    if datetime.now().astimezone(pytz.utc).time() < time(11,45,0):
        tm_max_date_value = datetime.now().date() - timedelta(days=1)
        tm_date_value = tm_max_date_value
    else:
        tm_max_date_value = datetime.now().date()
        tm_date_value = tm_max_date_value

    tm_time_limit = (
        datetime(2023, 1, 1, 5, 0, 0, tzinfo=pytz.utc)
        .astimezone(pytz.timezone('Europe/Paris')).time()
    )

    return tm_date_value, tm_max_date_value, tm_time_limit

@st.cache_data # prevent 'rerun' if raw data don't change
def clean_data_for_metrics(raw_data):
    '''
    Clean archived data recovered from hourly climatology API.
    Parameters:
    - raw_data : csv response from the API.
    Returns data in dictionnary compatible with 'display_observation_metrics' 
    function.
    '''
    # Import data in DataFrame
    df = pd.read_csv(StringIO(raw_data), sep=';')

    # Convert 'object' data to 'float'
    string_col = df.select_dtypes(include=['object']).columns
    for col in string_col:
        df[col] = df[col].str.replace(',', '.')
        df[col] = df[col].astype('float')
    # Replace Pandas 'NaN' with 'None'
    df = df.replace(np.nan, None)
    # Rename columns
    df = df.rename(
        columns={'NEIGETOT': 'sss', 'INS': 'insolh', 'PSTAT': 'pres'})
    # Lower columns names
    df.columns = df.columns.str.lower()
    # Set index with 'previous' and 'current' indication
    df['obs'] = ['previous_obs', 'current_obs']
    df = df.set_index('obs')
    # Convert units
    try:
        df['ff'] = round(df['ff'] * 3.6)
    except TypeError:
        pass
    try:
        df['vv'] = round((df['vv']/1000), 1)
    except TypeError:
        pass
    try:
        df['sss'] = round(df['sss'] * 100)
    except TypeError:
        pass
    try:
        df['pres'] = round(df['pres'])
    except TypeError:
        pass

    # Convert DataFrame to dictionnary
    data = df.to_dict('index')

    return data

# ------- Function for both 'current/past observation' sections in main page ------

@st.cache_data # prevent 'rerun' if observation data don't change 
def display_observation_metrics(data):
    '''
    Display metrics from observation data.
    Parameters :
    - data : dictionnary with data.
    Returns 'st.metrics'
    '''
    def delta(x, y):
        '''
        Calculate 'delta' parameter for 'st.metrics'
        '''
        if x == y:
            delta = None
        elif x is None or y is None:
            delta = None
        else:
            delta = x - y

        return delta
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            d = delta(data['current_obs']['t'], data['previous_obs']['t'])
            c = data['current_obs']['t']
            st.metric(
                label='Température',
                value=(f'{c:.1f} °C') if c is not None else None,
                delta=(f'{d:.1f} °C') if d is not None else None
            )
        with col2:
            d = delta(data['current_obs']['u'], data['previous_obs']['u'])
            c = data['current_obs']['u']
            st.metric(
                label='Humidité',
                value=(f'{c} %') if c is not None else None,
                delta=(f'{d:.0f} %') if d is not None else None
            )
        with col3:
            d = delta(data['current_obs']['ff'], data['previous_obs']['ff'])
            c = data['current_obs']['ff']
            st.metric(
                label='Vent',
                value=(f'{c:.0f} km/h') if c is not None else None,
                delta=(f'{d:.0f} km/h') if d is not None else None
            )
        with col4:
            d = delta(data['current_obs']['rr1'], data['previous_obs']['rr1'])
            c = data['current_obs']['rr1']
            st.metric(
                label='Précipitations 1h',
                value=(f'{c:.1f} mm') if c is not None else None,
                delta=(f'{d:.1f} mm') if d is not None else None
            )

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            d = delta(data['current_obs']['vv'], data['previous_obs']['vv'])
            c = data['current_obs']['vv']
            st.metric(
                label='Visibilité',
                value=(f'{c:.1f} km') if c is not None else None,
                delta=(f'{d:.1f} km') if d is not None else None
            )
        with col6:
            d = delta(data['current_obs']['sss'], data['previous_obs']['sss'])
            c = data['current_obs']['sss']
            st.metric(
                label='Neige',
                value=(f'{c:.0f} cm') if c is not None else None,
                delta=(f'{d:.0f} cm') if d is not None else None
            )
        with col7:
            d = delta(data['current_obs']['insolh'], data['previous_obs']['insolh'])
            c = data['current_obs']['insolh']
            st.metric(
                label='Ensoleillement',
                value=(f'{c:.0f} min') if c is not None else None,
                delta=(f'{d:.0f} min') if d is not None else None
            )
        with col8:
            d = delta(data['current_obs']['pres'], data['previous_obs']['pres'])
            c = data['current_obs']['pres']
            st.metric(
                label='Pression',
                value=(f'{c:.0f} hPa') if c is not None else None,
                delta=(f'{d:.0f} hPa') if d is not None else None
            )
        
        if 'validity_time' in data['current_obs']:
            st.caption(f'📅 {data['current_obs']['validity_time']}')

# ------- Functions for visualisation section in main page ------

@st.cache_data # prevent 'rerun' if 'raw_data' don't change
def clean_data_for_viz(raw_data):
    '''
    Clean archived data recovered from daily climatology API.
    Parameters:
    - raw_data : csv response from the API.
    Returns data in a DataFrame ready for plotting.
    '''
    # Import data in DataFrame
    df = pd.read_csv(StringIO(raw_data), sep=';', parse_dates=['DATE'])

    # Convert 'object' data to 'float'
    string_col = df.select_dtypes(include=['object']).columns
    for col in string_col:
        df[col] = df[col].str.replace(',', '.')
        df[col] = df[col].astype('float')
    # Lower columns names
    df.columns = df.columns.str.lower()

    return df

# ------- Main code of app : page config ------

st.set_page_config(page_title='Météo App', page_icon='🌤️',
                   initial_sidebar_state='expanded')

st.title('Météo app')

# st.session_state['id_station'] = ''

# ------- Main code of app : sidebar ------

with st.sidebar:
    
    st.markdown('## 🗺️ Commune')

    st.text_input(
        label='👉 1. Chercher',
        placeholder='Saisissez votre recherche...',
        value='',
        key='search_input'
    )

    st.selectbox(
        label='👉 2. Faites votre choix',
        options=search_municipality(st.session_state['search_input']),
        index=None,
        format_func=lambda x: f'{x['label']} ({x['context'].split(',')[0]})',
        key='selected',
        placeholder='Sélectionnez un résultat...'
    )
    
    def click_del():
        st.session_state['search_input'] = ''
        st.session_state['selected'] = None

    st.button('Effacer', on_click=click_del)
    
    if st.session_state['selected']:
        st.markdown('## 🗼 Station météo')
        id_station, station_open_date = get_display_station_info(st.session_state['selected'])


# ------- Main code of app : page ------
    
if st.session_state['selected']:

    st.markdown('#### 🌡️ Observations en temps réel')

    # Get data from API and display metrics
    current_data = get_current_data(id_station)
    display_observation_metrics(current_data)

    st.markdown('#### ⏲️ Observations à une date antérieure')

    with st.form('tm'):
        st.write('''
            **Remontez le temps** et afficher les relevés de la station 
            d'observation **à une date antérieure**.
        ''')

        # Get valide date and time parameters for inputs
        tm_date_value, tm_max_date_value, tm_time_limit = tm_input_parameters()

        col1, col2 = st.columns(2)
        with col1:
            tm_selected_date = st.date_input(
                label='1. Précisez une date',
                value=tm_date_value,
                max_value=tm_max_date_value
            )
        with col2:
            tm_selected_time = st.time_input(
                label='2. Précisez une heure',
                value=tm_time_limit,
                step=3600,
                label_visibility='visible'
            )

        tm_validate = st.form_submit_button('Valider')
    
        # Check if selected time respect Météo France API rules
        def check_datetime_limit():
            return ((tm_selected_date == tm_max_date_value)
                    and (tm_selected_time > tm_time_limit))

        if tm_validate:
            if not check_datetime_limit():
            # Set start and end datetime for the request
                tm_start_datetime = (
                    datetime.combine(tm_selected_date, tm_selected_time)
                    - timedelta(hours=1)
                ).strftime('%Y-%m-%dT%H:%M:%SZ')
                tm_end_datetime = (
                    datetime.combine(tm_selected_date, tm_selected_time)
                ).strftime('%Y-%m-%dT%H:%M:%SZ')

                # Get data from APIs
                tm_order = Client().order_hourly_weather_info(
                    id_station,
                    datetime_tz_convert(tm_start_datetime, 'local_to_utc'),
                    datetime_tz_convert(tm_end_datetime, 'local_to_utc')
                )
                tm_raw_data = Client().get_order_data(tm_order)

                # Prepare data and display metrics
                tm_data = clean_data_for_metrics(tm_raw_data)
                display_observation_metrics(tm_data)
            
            else:
                st.warning(f'L\'heure sélectionnée est trop récente : elle ne peut '
                       f'pas dépasser {tm_time_limit:%Hh%M}.')

    st.markdown('#### 📈 Historique des observations')

    # Create a descending list of years from the station opening until now
    viz_years_list = list(
        range(station_open_date.year, (datetime.now().year+1), 1))[::-1]
    
    with st.form('viz'):

        st.write('''
            Visualisez **l'évolution** d'une ou plusieurs **variable(s)** pour 
            **l'année** de votre choix. 
        ''')   
        
        viz_selected_year = st.selectbox(
            label='Sélectionnez une année', options=viz_years_list, index=1)
        
        viz_selected_variables = st.multiselect(
            label='Sélectionnez une variable',
            options=[v['label'] for k, v in viz_options_dict.items()],
            default=['Température'],
            placeholder='Sélectionnez une ou plusieurs variables...'
        )
        
        viz_validate = st.form_submit_button('Valider')


        if viz_selected_year == station_open_date.year:
            viz_start_datetime = f'{station_open_date}T00:00:00Z'
        else:
            viz_start_datetime = f'{viz_selected_year}-01-01T00:00:00Z'
        
        if viz_selected_year == datetime.now().year:
            viz_end_datetime = (
                datetime.now().date() - timedelta(days=1)
            ).strftime('%Y-%m-%dT00:00:00Z')
        else:
            viz_end_datetime = f'{viz_selected_year}-12-31T00:00:00Z'

        viz_order = Client().order_daily_weather_info(
            id_station, viz_start_datetime, viz_end_datetime)

        viz_raw_data = Client().get_order_data(viz_order)

        viz_data = clean_data_for_viz(viz_raw_data)

    # Delete Plots Button
    delete_plots_button = st.button('Supprimer les graphiques')

    if delete_plots_button:
    # Clear the existing plots
        st.empty()

    if viz_validate:

        for viz_variable in viz_selected_variables:
            for k, v in viz_options_dict.items():
                if viz_options_dict[k]['label'] == viz_variable:
                    variables_to_plot = viz_options_dict[k]['variables']

                    if viz_options_dict[k]['graph_type'] == 'line':
                        fig = px.line(
                            viz_data,
                            x='date',
                            y=variables_to_plot,
                            title=viz_variable,
                            labels={
                                'date': 'Date',
                                'value': f'Valeur ({viz_options_dict[k]['unit']})',
                                'variable': ''
                            }
                        )
                        fig.update_layout(legend=dict(x=0, y=1.1, orientation='h'))
                        st.plotly_chart(fig)

                    if viz_options_dict[k]['graph_type'] == 'bar':
                        fig = px.bar(
                            viz_data,
                            x='date',
                            y=variables_to_plot,
                            title=viz_variable,
                            labels={
                                'date': 'Date',
                                'value': f'Valeur ({viz_options_dict[k]['unit']})',
                                'variable': ''
                            }
                        )
                        fig.update_layout(legend=dict(x=0, y=1.1, orientation='h'))
                        st.plotly_chart(fig)
                        
else:
    st.info('''
        ### 📢 Aucune commune n'est sélectionnée !
        Pour afficher les informations et les relevés d\'une station 
        d\'observation, commencez par **sélectionner une commune**. 
            
        Pour cela, utilisez la **zone de recherche** située dans le **menu 
        latéral** puis **faites votre choix** parmi les **résultats proposés**.
    ''')