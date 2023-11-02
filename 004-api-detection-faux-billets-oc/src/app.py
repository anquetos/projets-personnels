# Importe les librairies
from dash import Dash, dcc, html, Input, Output
from dash import dash_table

import plotly.express as px

import base64
import io

import pandas as pd
import numpy as np

from pathlib import Path
import joblib

app = Dash(__name__)

# Pour déploiement render.com
server = app.server

app.title = 'Outil de détection de faux billets'

# Supprime l'erreur liée au bouton qui est généré par un autre callback
app.config.suppress_callback_exceptions = True

# Définit le chemin de l'application
app_folder = Path(__file__).parents[0]

# Définit le modèle à importer et son chemin
model_folder = app_folder / 'modele'
model_file = 'logistic-regression-gs.joblib'
model_path = Path(model_folder / model_file)

# Charge le modèle si le fichier 'joblib' est présent au bon emplacement 
if not model_folder.is_dir() or not model_path.is_file():
    clf = None
else:
    clf = joblib.load(model_path)

# Définit la mise en page de l'application
app.layout = html.Div(
    children=[
    
        html.Link(
            rel='stylesheet',
            href='/assets/font-ubuntu.css'
        ),

        html.Header(
            style={
                'display': 'flex',
                'align-items': 'center',
                'height': '90px',
                'background': '#415F58',
                'margin': '-10px'
            },
            children=[
                html.Div(
                    html.Img(
                        src=app.get_asset_url('cash-coin.svg'),
                        style={
                            'filter': 'invert(1)',
                            'width': '32px',
                            'height': '32px'
                        }
                    ),
                    style={
                        'margin-left': '5%',
                        'margin-right': '1%'
                    }
                ),

                html.Div(
                    [
                        html.H1('Outil de détection de faux billets',
                                style={'margin': '0px'}),
                        html.Div('Le Machine Learning contre la fraude !',
                                 style={'font-weight': 'lighter'})
                    ],
                    style={
                        'align-self': 'center',
                        'textAlign': 'left',
                        'color': 'white'
                    }
                ),

                html.Div(
                    html.A(
                        html.Img(
                            src=app.get_asset_url('plotly_logo_dark.png'),
                            style={
                                'width' :'auto',
                                'height': '36px'
                            }
                        ),
                        href='https://dash.plotly.com/'
                    ),
                    style={
                        'margin-left': 'auto',
                        'margin-right': '1%'
                    }
                ),

                html.Div(
                    html.A(
                        html.Img(
                            src=app.get_asset_url('github.svg'),
                            style={
                                'filter': 'invert(1)',
                                'width': '26px',
                                'height': '26px'
                            }
                        ),
                        href='https://github.com/anquetos'
                    ),
                    style={
                        'margin-left': '0px',
                        'margin-right': '2%'
                    }
                )
            ]
        ),

        html.Div(
            [
                html.H2('A propos'),
                html.P(
                    '''
                    Cet outil est un algorithme de détection automatique de
                    faux billets permettant de lire un fichier contenant les
                    dimensions de plusieurs billets et de déterminer s'ils sont
                    authentiques en se basant sur leurs seules dimensions.
                    '''
                ),
                html.P(
                    '''
                    L\'algorithme utilise un modèle de régression linéaire
                    entraîné et optimisé grâce à un fichier d\'exemple
                    contenant 1500 billets dont 1000 étaient vrais et 500
                    étaient faux.
                    '''
                ),
                html.P(
                    [
                        'Il a été développé en ',
                        html.B('Python '),
                        'grâce à la librairie de ',
                        html.I('Machine Learning '),
                        html.B('scikit-learn', style={'font-family':'Ubuntu Mono'}),
                        '.'
                    ],
                ),

                html.H3('Caractéristiques géométriques des billets'),

                html.Div(
                    style={
                        'display': 'flex',
                        'align-items': 'center',
                        'margin-top': '0%',
                        'margin-bottom': '0%'
                    },
                    children=[
                        html.Div(
                            html.Img(
                                src=app.get_asset_url('banknote-dimensions.svg'),
                                style={
                                    'width': '80%',
                                    'height': 'auto',
                                }
                            )
                        ),
                        html.Ol(
                            [
                                html.Li('height_left (mm)'),
                                html.Li('height_right (mm)'),
                                html.Li('length (mm)'),
                                html.Li('diagonal (mm)'),
                                html.Li('margin_up (mm)'),
                                html.Li('margin_low (mm)')
                            ]
                        )
                    ]
                ),
                
                html.Hr(style={
                    'opacity': '50%',
                    'border':'0px',
                    'border-top':'1px solid',
                    'margin-top': '3%'
                })
            ],
            style={
                'width': '62%',
                'margin':'auto',
                'text-align': 'justify'
            }
        ),

        html.Div(
            id='l-outil',
            children=[
                html.H2('L\'outil'),
                html.Div(
                    'Vérifier si tous vos billets sont authentiques',
                    style={
                        'font-weight': '350',
                        'text-align': 'center'
                    }
                )
            ],
            style={
                'width': '62%',
                'margin':'auto'
            }
        ),

        html.Div(
            dcc.Upload(
                id='upload-csv',
                children=html.Div(
                    [
                        ('Glisser-déposer ou '),
                        html.A(html.B('ouvrir un fichier ')),
                        ('au format CSV')
                    ],
                    style={
                        'height': '48px',
                        'lineHeight': '48px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        'textAlign': 'left',
                        'margin-top': '1%',
                        'margin-bottom': '3%',
                        'padding-left': '3%',
                        'color':'#5d5c5c',
                        'border-color': '#D1D0D0',
                        'background': '#F0EFEF'
                    }
                )
            ),      
            style={
                'width': '62%',
                'margin':'auto'
                }
        ),

        html.Div(
            [
                html.Div(id='csv-filename'),
                html.Div(id='csv-data-table'),
                html.Div(id='csv-information'),
                html.Div(id='detect-results', style={'visibility': 'hidden'})

            ],
            style={
                'width': '62%',
                'margin':'auto',
                }
        ),

        html.Footer(
            children=[
                html.Div(
                    '10/2023 - Application réalisée par Thomas Anquetil',
                    style={
                        'color': 'white',
                        'font-size': 14,
                        }
                ),
                html.Div(
                    html.A(
                        html.Img(
                            src=app.get_asset_url('envelope.svg'),
                            style={
                                'filter': 'invert(1)',
                                'width': '18px',
                                'height': '18px',
                            }
                        ),
                        href='mailto:t.anquetil@proton.me'
                    ),
                    style={'margin-left': '1%'}
                ),
                html.Div(
                    html.A(
                        html.Img(
                            src=app.get_asset_url('linkedin.svg'),
                            style={
                                'filter': 'invert(1)',
                                'width': '18px',
                                'height': '18px'
                            }
                        ),
                        href='https://www.linkedin.com/in/thomas-anquetil-132a73123'
                    ),
                    style={'margin-left': '1%'}
                ),
            ],
            style={
                'display': 'flex',
                'align-items': 'center',
                'height': '42px',
                'background': '#415F58',
                'margin': '-10px',
                'margin-up': '10%',
                'justify-content': 'center'
            },
        )
    ],
    style={
        'width': '99.8%',
        'color': '#282727',
        'margin': 'auto'
    }
)

# Affiche le nom du fichier analysé
@app.callback(
        Output('csv-filename', 'children'),
        Input('upload-csv', 'filename')
)

def update_csv_filename(filename):
    if filename is not None:
        return html.H3(['Fichier de données : ', filename])

# Affiche le contenu du fichier
@app.callback(
        Output('csv-data-table', 'children'),
        Input('upload-csv', 'contents')
)

def update_csv_data_table(contents):
    if contents is not None:
        # Importe le fichier csv dans un DataFrame
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        global df
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        return dash_table.DataTable(
                        data=df.to_dict('records'),
                        columns=[
                            {'name': col, 'id': col} for col in df.columns
                        ],
                        page_size=10)

# Vérifie que les données à analyser sont complètes                
@app.callback(
        Output('csv-information', 'children'),
        Output('detect-results', 'style'),
        Input('csv-data-table', 'children')
)
    
def update_csv_information(children):

    # Affiche un message d'erreur si le modèle n'a pas été chargé
    if clf is None:
            div =  html.Div(
                html.Div(
                    children=[
                        html.B('Impossible de charger le modèle ! '),
                        ('Répertoire ou fichier joblib inexistant.')
                    ],
                    style={
                        'height': '48px',
                        'lineHeight': '48px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        'textAlign': 'left',
                        'margin-top': '1%',
                        'margin-bottom': '3%',
                        'padding-left': '3%',
                        'color':'#A91F1F',
                        'border-color': '#EB9393',
                        'background': '#F4C1C1',
                    }
                )
            )
            
            detect_results_style = {'visibility':'hidden'}

            return div, detect_results_style

    elif children is not None:
     
        # Initialise le set des colonnes que doit contenir le fichier à tester
        features = {'diagonal', 'height_left', 'height_right', 'margin_low',
                    'margin_up', 'length', 'id'}
        
        # Crée un set avec le nom des colonnes du DataFrame
        df_features = set(df.columns)
        
        # Vérifie la présence de toutes les colonnes
        if len(features - df_features) != 0:
            
            div = html.Div(
                children=[
                    html.B('Fichier non valide ! '),
                    ('Il manque la ou les variable(s) suivante(s) : '),
                    html.B(f'{", ".join(features - df_features)}')
                ],
                style={
                    'height': '48px',
                    'lineHeight': '48px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '5px',
                    'textAlign': 'left',
                    'margin-top': '1%',
                    'margin-bottom': '3%',
                    'padding-left': '3%',
                    'color':'#A91F1F',
                    'border-color': '#EB9393',
                    'background': '#F4C1C1',
                }
            )

            detect_results_style = {'visibility':'hidden'}

        # Vérifie l'absence de valeurs manquantes
        elif df.isna().any().any():

            div = html.Div(
                children=[
                    html.B('Fichier non valide ! '),
                    (
                        f'Il manque des données dans la ou les variable(s) '
                        f'suivante(s) : '),
                    html.B(
                        f'{", ".join(df.columns[df.isna().any()].to_list())}'
                    )
                ],
                style={
                    'height': '48px',
                    'lineHeight': '48px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '5px',
                    'textAlign': 'left',
                    'margin-top': '1%',
                    'margin-bottom': '3%',
                    'padding-left': '3%',
                    'color':'#A91F1F',
                    'border-color': '#EB9393',
                    'background': '#F4C1C1',
                }
            )

            detect_results_style = {'visibility':'hidden'}

        else:

            div = (
                html.Div(
                    children=[
                        html.B('Fichier valide ! '),
                        ('Les données ont été importées avec succès.'),
                    ],
                    style={
                        'height': '48px',
                        'lineHeight': '48px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        'textAlign': 'left',
                        'margin-top': '1%',
                        'margin-bottom': '1%',
                        'padding-left': '3%',
                        'color':'#217338',
                        'border-color': '#94E0AA',
                        'background': '#DBF5E3'
                    }
                ),
                html.Div(
                    html.Button(
                        id='detect-button',
                        children='Détecter !',
                        n_clicks=None,
                        style={
                            'height': '48px',
                            'width': '20%',
                            'lineHeight': '48px',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin-top': '1%',
                            'margin-bottom': '3%',
                            'font-family':'ubuntu',
                            'font-size': 16,
                            'color':'white',
                            'background-color': '#415F58',
                            
                        }
                    ),
                    style={
                        'display': 'flex',
                        'justify-content': 'center',
                        'align-items': 'center'
                    }
                )
            )

            detect_results_style = {'visibility':'visible'}
        
        return div, detect_results_style
    
    return None, None

# Affiche les résultats de la détection
@app.callback(
        Output('detect-results', 'children'),
        Input('detect-button', 'n_clicks')
)

def update_detect_results(n_clicks):
    
    if n_clicks is not None:

        ids = df['id']
        X = df.drop(columns='id')
        y_pred = clf.predict(X)

        # Crée un DataFrame contenant les résultats de la prédiction
        global df_results

        df_results = pd.DataFrame(
            zip(
                ids, y_pred, clf.predict_proba(X)[:, 0],
                clf.predict_proba(X)[:, 1]
            ),
            columns=['id', 'is_fake', 'prob_0', 'prob_1']
            )
        
        df_results['is_fake'] = df_results['is_fake'].map({0: False, 1: True})

        df_results['probability_estimates'] = np.where(
            df_results['is_fake'], df_results['prob_1'], df_results['prob_0'])

        df_results = df_results.drop(columns=['prob_0', 'prob_1'])

        # Affiche les résultats de la détection
        fake_banknote_list = list(
            df_results.loc[df_results['is_fake'] == True, 'id'])
        
        global nb_fake
        nb_fake = len(fake_banknote_list)

        fake_banknote_list = ', '.join(fake_banknote_list)
        if nb_fake == 0:
            fake_banknote_list = 'None'

        return html.Div(
            children=[
                html.H2('Résultats'),

                html.H3('Faux billets'),

                html.Div(
                    children=[
                        html.B(f'{nb_fake} faux billets détectés ! '),
                        (f'Id : {fake_banknote_list}.')
                    ],
                    style={
                        'height': '48px',
                        'lineHeight': '48px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'border-color': '#D1D0D0',
                        'background': '#F0EFEF'
                    }
                ),

                html.H3('Statistiques de la détection'),

                html.Div(
                    (f'Résultats détaillés de l\'algorithme pour chacun '
                    f'des billets.'),
                    style={
                        'margin-top': '1%',
                        'margin-bottom': '3%',
                    }
                ),
   
                html.Div(
                    dash_table.DataTable(
                        data=df_results.to_dict('records'),
                        columns=[
                            {'name': col, 'id': col} for col in df_results.columns
                        ],
                        page_size=10
                    ),
                    style={
                        'width': '50%',
                        'margin': 'auto',
                        'margin-top': '1%',
                        'margin-bottom': '3%'
                        }
                ),

                html.Div(
                    ('Avec :'),
                    style={
                        'margin-bottom': '0%'
                    }

                ),

                html.Ul(
                    [
                        html.Li([
                            html.B('id :'),
                            ' identifiant du billet ;'
                        ]),
                        html.Li([
                            html.B('is_fake :'),
                            ' le billet est-il détecté comme étant faux ;'
                        ]),
                        html.Li([
                            html.B('probability_estimates :'),
                            ' la probabilité que la prédiction faite soit exacte.'
                     ])
                    ],
                    style={
                        'margin-top': '0%'
                    }
                ),

                html.H3('Visualisation des caractéristiques'),

                dcc.Dropdown(
                    id='features-dropdown',
                    options=['diagonal', 'height_left', 'height_right',
                             'margin_low', 'margin_up', 'length'],
                    value=['margin_low', 'length'],
                    multi=True
                ),

                dcc.Graph(
                    id='features-graph',
                    style={
                        'width': '75%',
                        'margin': 'auto'
                    }
                ),
                html.Div(
                    html.A(
                        'Sélectionner un autre fichier',
                        href='#l-outil'  
                    ),
                    style={
                        'textAlign': 'center',
                        'margin-top': '1%',
                        'margin-bottom': '3%',
                        }
                )
            ]
        )
    
@app.callback(
        Output('features-graph', 'figure'),
        Input('features-dropdown', 'value')
)

def update_graph_results(dims):

    df['is_fake'] = df_results['is_fake']
    if nb_fake == 0:
        fig = px.scatter_matrix(df, dimensions=dims, hover_name='id')
    else:
        fig = px.scatter_matrix(df, dimensions=dims, hover_name='id',
                                color='is_fake')
    
    return fig


if __name__ == '__main__':
    app.run(debug=True)