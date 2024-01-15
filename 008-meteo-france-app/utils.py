# Import libraries
import requests
from geopy.distance import geodesic
from geopy import distance


# Functions used in the app

def search_municipality(query: str):
    '''
    Search French municipality with the Adresse API and returns a list of
    tuples (label: label and context of municipality, value: coordinates of 
    municipality).

    Parameters:
    - query : string to look for.

    Returns a maximum of 5 results in a dictionnay.
    '''
    # Requests Adresse API
    r = requests.get(
        'https://api-adresse.data.gouv.fr/search/',
        params={
            'q': query,
            'type': 'municipality',
            'limit': 5,
            'autocomplete': 1
        }
    )
    # Check if the request as succeeded
    if r.status_code == 200:
        # Parse the response in dictionnary
        results = r.json()['features']
        # first element will be shown in search, second is returned from 
        # component
        data = [
            {
                'label': result['properties']['label'],
                'context': result['properties']['context'],
                'coordinates': result['geometry']['coordinates'][::-1]
            }

            for result in results
        ]

        return data
    
    else:

        return []
    

def find_nearest_stations(df, lat_lon):
    '''
    Calculate the geodesic distance between coordinates (defined in 'latitude' 
    and 'longitude' columns) and a specified [lat, lon] list for each row of 
    the DataFrame.

    Parameters :
    - df : DataFrame including latitude and longitude columns ;
    - lat_lon : pair of [latitude, longitude] in a list.

    Returns the 5 nearest stations information in dictionnary.
    '''
    if ('latitude' and 'longitude' in df.columns) and lat_lon:
        df['distance'] = df.apply(
            lambda x: distance.distance(
                [x['latitude'], x['longitude']],
                lat_lon).km,
                axis='columns'
        )

        data = df.nsmallest(5, 'distance').to_dict('records')

        return data    


def reverse_geocoding(lat_lon):
    '''
    Apply reverse geocoding from latitude and longitude.

    Parameters :
    - lat_lon : pair of [latitude, longitude] in a list.

    Returns the city and the context.
    '''
    lat = lat_lon[0]
    lon = lat_lon[1]
    x = len(str(lat))

    while True:

        url = 'https://api-adresse.data.gouv.fr/reverse/'
        payload = {
            'lon': lon,
            'lat': str(lat)[:x],
            'type': 'street',
            'limit': 1
        }
        r = requests.get(url, params=payload)
        result = r.json()['features']

        if result:
            result = result[0]
            break

        x -= 1

    data = {
            'city': result['properties']['city'],
            'context': result['properties']['context']
        }
            
    return data