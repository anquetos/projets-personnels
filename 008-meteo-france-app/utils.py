# Import libraries
import requests

# Functions used in the app


def search_municipality(query: str):
    '''
    Search French municipality with the Adresse API and returns a list of
    tuples (label: label and context of municipality, value: coordinates of 
    municipality).
    Parameters:
    - query : string to look for.
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
        return [
            (
                (
                    f'{result['properties']['label']} ('
                    f'{result['properties']['context']})'
                ),
                result['geometry']['coordinates']
            )
            for result in results
        ]

    else:
        return []


# def get_weather_stations():
#     url = 'https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations'
#     payload={
#         'apikey': 'eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJBbnF1ZXRvc0BjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6IkFucXVldG9zIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6Njg0OSwidXVpZCI6ImNlZjUzMmRlLWYyMWYtNGNkMy1hZWY4LWM1YTI4MjAxNjgxNSJ9LCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnI6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsiNTBQZXJNaW4iOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJEb25uZWVzUHVibGlxdWVzQ2xpbWF0b2xvZ2llIiwiY29udGV4dCI6IlwvcHVibGljXC9EUENsaW1cL3YxIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoidjEiLCJzdWJzY3JpcHRpb25UaWVyIjoiNTBQZXJNaW4ifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiRG9ubmVlc1B1YmxpcXVlc09ic2VydmF0aW9uIiwiY29udGV4dCI6IlwvcHVibGljXC9EUE9ic1wvdjEiLCJwdWJsaXNoZXIiOiJiYXN0aWVuZyIsInZlcnNpb24iOiJ2MSIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9XSwidG9rZW5fdHlwZSI6ImFwaUtleSIsImlhdCI6MTcwNDcyMjk2OCwianRpIjoiYzkxZGNmM2UtMWE2Zi00ZTI5LWE2YjgtNzJkY2Y3ZDk5MTViIn0=.ROG4y7WRGJSzUSDbtLyihE9lFsJo-GnIUCtXRvSXOFy9-ST1VHBqRssmRrufu4XZgIkQgV9-4GxzpL4jbBElUpA8wSZbFbumEzUEAVQgDrTHsqxlTq57t0fzU8_TiTzTQANEKU2ugEpLsT1lzjPR3M2xNIqXecwliMUf2HktJk5w9sp8WEeByFQ4OO3RS65hjrwoCoVWQXrIub6w288yrbcsyN8BR4DAlX9NBIsUH2j9-nVc4uRrg7bM_2o1Zl4P2kE4EDfwbYVQ0oEmCu_5ghhHXqHKesoAjKIB9bBBTT5nphgtP9jlUe88tgEvAqY7FQa_EnmLk-8zbNnVxDSm6g=='
#     }

#     r = requests.get(url, params=payload)

#     if r.status_code == 200:
#         return pd.read_csv(io.StringIO(r.text), sep=';')
#     else:
#         return []


# def find_closest_weather_station(coordinates):
#     df = get_weather_stations()
#     df['coordinates'] = coordinates

#     return df