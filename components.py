from dash import html, dcc
import dash_bootstrap_components as dbc


# Créer les boutons à partir des positions ++ gérer les deux pages via le fichier texte
def create_button(aiguillage_id, pos):
    """Crée un bouton avec image positionné"""
    return html.Button(
        html.Img(
            id=f'img-{aiguillage_id}',
            src=f'/assets/{pos['droit']}.png',  # Image du bouton
            style={
                'width': f'{pos['w']}px',
                'height': f'{pos['h'] }px',
                'object-fit': 'contain',
                'pointer-events': 'none'
            }
        ),
        id=f'btn-{aiguillage_id}',
        n_clicks=0,
        className='button-aiguillage',
        style={
            'position': 'absolute',
            'left': f'{pos['x']}px',
            'top': f'{pos['y']}px',
            'background': 'transparent',
            'border': 'none',
            'cursor': 'pointer',
            'padding': '0'
        }
    )

STATE_BTN_DROIT = {
    'background-color': '#6c757d', 'color': 'white', 'border': 'none',
    'border-radius': '8px', 'padding': '12px 8px', 'cursor': 'pointer',
    'width': '85px', 'text-align': 'center', 'transition': 'all 0.3s ease',
    'font-family': 'Arial, sans-serif'
}
STATE_BTN_DEVIE = {
    'background-color': '#28a745', 'color': 'white', 'border': 'none',
    'border-radius': '8px', 'padding': '12px 8px', 'cursor': 'pointer',
    'width': '85px', 'text-align': 'center', 'transition': 'all 0.3s ease',
    'font-family': 'Arial, sans-serif',
    'box-shadow': '0 0 10px rgba(40,167,69,0.5)'
}

def create_state_tab(positions, dashboard_data):
    """Crée un onglet avec une colonne par puce I2C, boutons cliquables."""
    # Grouper par I2C, trié par adresse_spec
    by_i2c = {}
    for aig_id, data in dashboard_data.items():
        i2c = data['i2c']
        if i2c not in by_i2c:
            by_i2c[i2c] = []
        by_i2c[i2c].append((aig_id, data['spec']))

    # Aiguillages sans mapping I2C → colonne "?" à part
    mapped = set(dashboard_data.keys())
    unmapped = [aig_id for aig_id in positions.keys() if aig_id not in mapped]

    columns = []
    for i2c_addr in sorted(by_i2c.keys()):
        aigs = sorted(by_i2c[i2c_addr], key=lambda x: x[1])
        buttons = [
            html.Div(
                html.Button(
                    [html.Div(aig_id, style={'font-weight': 'bold', 'font-size': '13px'}),
                     html.Div('DROIT', style={'font-size': '10px', 'margin-top': '4px'})],
                    id=f'state-btn-{aig_id}',
                    n_clicks=0,
                    style=STATE_BTN_DROIT
                ),
                style={'margin': '4px'}
            )
            for aig_id, _ in aigs
        ]
        columns.append(html.Div(
            [html.Div(i2c_addr, style={
                'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center',
                'margin-bottom': '8px', 'color': '#495057',
                'border-bottom': '2px solid #dee2e6', 'padding-bottom': '4px'
            })] + buttons,
            style={'display': 'flex', 'flex-direction': 'column',
                   'margin': '10px', 'min-width': '100px'}
        ))

    if unmapped:
        buttons = [
            html.Div(
                html.Button(
                    [html.Div(aig_id, style={'font-weight': 'bold', 'font-size': '13px'}),
                     html.Div('DROIT', style={'font-size': '10px', 'margin-top': '4px'})],
                    id=f'state-btn-{aig_id}',
                    n_clicks=0,
                    style=STATE_BTN_DROIT
                ),
                style={'margin': '4px'}
            )
            for aig_id in unmapped
        ]
        columns.append(html.Div(
            [html.Div('—', style={
                'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center',
                'margin-bottom': '8px', 'color': '#adb5bd',
                'border-bottom': '2px solid #dee2e6', 'padding-bottom': '4px'
            })] + buttons,
            style={'display': 'flex', 'flex-direction': 'column',
                   'margin': '10px', 'min-width': '100px'}
        ))

    return html.Div(columns, style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '20px'})


def create_i2c_tabs(dashboard_data):
    """Crée un onglet par puce I2C avec un voyant par aiguillage"""
    # Grouper par adresse I2C, trié par adresse_spec
    by_i2c = {}
    for aig_id, data in dashboard_data.items():
        i2c = data['i2c']
        if i2c not in by_i2c:
            by_i2c[i2c] = []
        by_i2c[i2c].append((aig_id, data['spec']))

    tabs = []
    for i2c_addr in sorted(by_i2c.keys()):
        aigs = sorted(by_i2c[i2c_addr], key=lambda x: x[1])
        leds = []
        for aig_id, spec in aigs:
            leds.append(html.Div([
                html.Div(
                    id=f'led-{aig_id}',
                    style={
                        'width': '30px',
                        'height': '30px',
                        'border-radius': '50%',
                        'background-color': '#dc3545',
                        'margin': '0 auto 6px auto',
                        'box-shadow': '0 0 5px rgba(0,0,0,0.3)',
                        'transition': 'all 0.3s ease'
                    }
                ),
                html.Div(aig_id, style={'font-size': '11px', 'text-align': 'center'}),
                html.Div(f'0x{spec:02X}', style={'font-size': '10px', 'color': '#888', 'text-align': 'center'}),
            ], style={'margin': '8px', 'width': '55px'})
            )
        tabs.append(dbc.Tab(
            label=i2c_addr,
            children=[html.Div(leds, style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '15px'})]
        ))

    return dbc.Tabs(tabs)



TRIAGE_BTN_STYLE = {
    'width': '70px', 'height': '52px',
    'background-color': '#0d6efd', 'color': 'white',
    'border': 'none', 'border-radius': '6px',
    'font-size': '15px', 'font-weight': 'bold',
    'cursor': 'pointer', 'transition': 'all 0.2s ease',
    'box-shadow': '0 2px 6px rgba(13,110,253,0.4)'
}


def create_triage_column(triage_data):
    """Colonne de boutons T75→T71 pour le tableau de triage."""
    keys_sorted = sorted(triage_data.keys(), reverse=True)  # T75 en haut
    buttons = [
        html.Button(key, id=f'triage-btn-{key}', n_clicks=0, style=TRIAGE_BTN_STYLE)
        for key in keys_sorted
    ]
    return html.Div(buttons, style={
        'display': 'flex', 'flex-direction': 'column',
        'gap': '10px', 'padding': '10px',
        'align-self': 'flex-start', 'margin-top': '10px',
        'width': '90px'
    })


def layout(positions, dashboard_data, triage_data):
    layout = html.Div([
        dcc.Store(id='aiguillages-state', data={aig_id: False for aig_id in positions.keys()}),
        dbc.Tabs([
            dbc.Tab(
                label="Niveau 0",
                tab_id="0",
                children=[html.Div(
                    style={
                        'position': 'relative',
                        'width': '1050px', 'height': '620px',
                        'background-image': 'url("assets/planche haute2025.png")',
                        'background-size': 'contain',
                        'background-repeat': 'no-repeat',
                        'background-position': 'top-left',
                        'margin': 'auto', 'border': '0px'
                    },
                    children=[
                        *[create_button(aig_id, pos)
                          for aig_id, pos in positions.items() if pos["table"] == "h"]
                    ]
                )]
            ),
            dbc.Tab(
                label="Niveau -1",
                tab_id="-1",
                children=[html.Div([
                    # Spacer gauche = même largeur que la colonne triage (symétrie)
                    html.Div(style={'width': '90px', 'flex-shrink': '0'}),
                    # Image planche avec boutons aiguillages
                    html.Div(
                        style={
                            'position': 'relative',
                            'width': '1050px', 'height': '620px',
                            'background-image': 'url("assets/planche basse2025.png")',
                            'background-size': 'contain',
                            'background-repeat': 'no-repeat',
                            'background-position': 'top-left',
                            'flex-shrink': '0'
                        },
                        children=[
                            *[create_button(aig_id, pos)
                              for aig_id, pos in positions.items() if pos["table"] == "b"]
                        ]
                    ),
                    # Colonne boutons triage
                    create_triage_column(triage_data),
                ], style={
                    'display': 'flex',
                    'justify-content': 'center',
                    'align-items': 'flex-start'
                })]
            ),
            dbc.Tab(
                label="États",
                tab_id="states",
                children=[create_state_tab(positions, dashboard_data)]
            ),
        ]),
        html.Div(
            id='output-info',
            style={'margin-top': '10px', 'text-align': 'center', 'font-size': '16px'}
        ),
    ])

    return layout