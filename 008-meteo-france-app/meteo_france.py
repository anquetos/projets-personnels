# Module with functions to resquest the following Météo France APIs :
# - Observation data ;
# - Climatological data.
#
# The first part about implementation for a continuous authentication client
# is from Météo France FAQ (https://portail-api.meteofrance.fr/web/fr/faq).
#
# It is necessary to have an APPLICATION_ID. see 'Mes APIs > Token' on website.

#------------------------------------------------------------
# First part from Météo France FAQ
#------------------------------------------------------------

import requests
from datetime import datetime
import pytz

# Unique application id : you can find this in the curl's command to generate
# jwt token 
APPLICATION_ID = 'NFpkTkNZa2lCVE0xVHhYS3Azbk9YcF9hbTZzYTpoVkZFUzVEeHU2dVRPajhqQm9BYm1ZenJ6dU1h'

# Url to obtain acces token
TOKEN_URL = "https://portail-api.meteofrance.fr/token"

class Client(object):

    def __init__(self):
        self.session = requests.Session()


    def request(self, method, url, **kwargs):
        # First request will always need to obtain a token first
        if 'Authorization' not in self.session.headers:
            self.obtain_token()

        # Optimistically attempt to dispatch request
        response = self.session.request(method, url, **kwargs)
        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = self.session.request(method, url, **kwargs)

        return response


    def token_has_expired(self, response):
        status = response.status_code
        content_type = response.headers['Content-Type']
        repJson = response.text
        if status == 401 and 'application/json' in content_type:
            repJson = response.text
            if 'Invalid JWT token' in repJson['description']:

                return True
            
        return False


    def obtain_token(self):
        # Obtain new token
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': 'Basic ' + APPLICATION_ID}
        access_token_response = requests.post(
            TOKEN_URL,
            data=data,
            verify=True,
            allow_redirects=False,
            headers=headers
        )
        token = access_token_response.json()['access_token']
        # Update session with fresh token
        self.session.headers.update({'Authorization': 'Bearer %s' % token})

#------------------------------------------------------------
# Below functions have been added to make the needed requests
#------------------------------------------------------------

    def get_stations_list(self):
        '''
        Get the list of observation stations.
        '''
        self.session.headers.update({'Accept': 'application/json'})
        response = self.request(
            method='GET',
            url='https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations'
        )

        return response.text
    

    def get_observation(self, id_station: str, date):
        '''
        Get available data for one observation station at a specific
        date-time for the current year. If date-time not indicated, actual
        date-time returned.
        Parameters :
        - id_station : id number (string) ;
        - date : date of observation (string) in ISO 8601 format with
        TZ UTC AAAA-MM-JJThh:00:00Z.
        '''
        self.session.headers.update({'Accept': 'application/json'})
        payload={
            'id_station': id_station,
            'date': date,
            'format': 'json'
        }
        response = self.request(
            method='GET',
            url='https://public-api.meteofrance.fr/public/DPObs/v1/station/horaire',
            params=payload
        )

        response = response.json()[0]

        # Convert date and time information from UTC to local timezone
        time_utc = datetime.strptime(
            response['validity_time'], "%Y-%m-%dT%H:%M:%SZ")
        # Set UTC timezone
        utc_timezone = pytz.timezone('UTC')
        # Add timezone to UTC time
        time_utc = utc_timezone.localize(time_utc)
        # Convert UTC time to local
        local_tz = pytz.timezone('Europe/Paris')
        time_local = time_utc.astimezone(local_tz).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Convert temperature from Kelvin to Celsisus
        if response['t'] is not None:
            t = round(response['t'] - 273, 1)
        else:
            t = None

        # Convert mean wind speed from m/s to km/h
        if response['ff'] is not None:
            ff = round(response['ff'] * 3.6, 0)
        else:
            ff = None

        # Build data
        data = {
            'validity_time': time_local,
            't': t,
            'u': response['u'],
            'ff': ff,
            'rr1': response['rr1'],
            'insolh': response['insolh']
        }

        return data
    

    def order_daily_weather_info(
            self, id_station: str, start_date: str, end_date: str):
        '''
        Get an order number for asynchronous download of daily weather
        information for one observation station in a period of date.
        Parameters :
        - id_station : id number (string) ;
        - start_date : start of period for the order (string) in ISO 8601 format
        with TZ UTC AAAA-MM-JJThh:00:00Z ;
        - end_date : end of period for the order (string) in ISO 8601 format
        with TZ UTC AAAA-MM-JJThh:00:00Z.
        '''
        self.session.headers.update({'Accept': 'application/json'})
        payload={
            'id-station': id_station,
            'date-deb-periode': start_date,
            'date-fin-periode': end_date
        }
        response = self.request(
            method='GET',
            url='https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne',
            params=payload
        )

        return response.json()['elaboreProduitAvecDemandeResponse']['return']
    

    def get_daily_weather_info(self, order_number: str):
        '''
        Get the weather information data for a specific order generated with
        'order_daily_weather_info() function'.
        Parameter :
        - order_number (string).
        '''
        self.session.headers.update({'Accept': 'application/json'})
        payload={'id-cmde': order_number}
        response = self.request(
            method='GET',
            url='https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier',
            params=payload
        )

        return response.text

def main():
    client=Client()


if __name__ == '__main__':
    main()