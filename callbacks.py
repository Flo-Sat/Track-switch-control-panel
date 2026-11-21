import time
import dash
from dash import html, Input, Output, State
import i2c_manager
from components import STATE_BTN_DROIT, STATE_BTN_DEVIE

# Délai supplémentaire entre deux aiguillages d'une séquence triage (en secondes)
# pulse() ajoute déjà 0.3 s ; ce délai s'ajoute entre chaque aiguillage
INTER_PULSE_DELAY = 0.5


def register_callbacks(app, positions, dashboard_data, triage_data):

    i2c_manager.init_com(dashboard_data)
    i2c_manager.reset_all(dashboard_data,positions)

    @app.callback(
        [Output(f'img-{aig_id}', 'src')           for aig_id in positions.keys()] +
        [Output(f'state-btn-{aig_id}', 'children') for aig_id in positions.keys()] +
        [Output(f'state-btn-{aig_id}', 'style')    for aig_id in positions.keys()] +
        [Output('aiguillages-state', 'data'),
         Output('output-info', 'children')],
        [Input(f'btn-{aig_id}', 'n_clicks')        for aig_id in positions.keys()] +
        [Input(f'state-btn-{aig_id}', 'n_clicks')  for aig_id in positions.keys()] +
        [Input(f'triage-btn-{key}', 'n_clicks')    for key in triage_data.keys()],
        State('aiguillages-state', 'data'),
        prevent_initial_call=True
    )
    def update_aiguillages(*args):
        ctx = dash.callback_context
        current_state = args[-1]

        def _btn_children(aig_id):
            label = 'DÉVIÉ' if current_state.get(aig_id, False) else 'DROIT'
            return [
                html.Div(aig_id, style={'font-weight': 'bold', 'font-size': '13px'}),
                html.Div(label,  style={'font-size': '10px', 'margin-top': '4px'})
            ]

        def _build_outputs():
            images       = [f'/assets/{pos["devie"] if current_state[a] else pos["droit"]}.png'
                            for a, pos in positions.items()]
            btn_children = [_btn_children(a) for a in positions.keys()]
            btn_styles   = [STATE_BTN_DEVIE if current_state.get(a, False) else STATE_BTN_DROIT
                            for a in positions.keys()]
            return images, btn_children, btn_styles

        def _pulse_aig(aig_id, devie):
            """Envoie la commande I2C pour un aiguillage.
            Si positions[aig_id]['inverse'] est True, OLATA et OLATB sont échangés."""
            if aig_id in dashboard_data:
                i2c_addr = int(dashboard_data[aig_id]['i2c'], 16)
                spec     = dashboard_data[aig_id]['spec']
                inverse  = positions.get(aig_id, {}).get('inverse', False)
                effective_devie = devie ^ inverse  # XOR : inverse la logique si flag actif
                i2c_manager.pulse(i2c_addr, i2c_manager.OLATB if effective_devie else i2c_manager.OLATA, spec)

        if not ctx.triggered:
            images, btn_children, btn_styles = _build_outputs()
            return images + btn_children + btn_styles + [current_state, ""]

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # --- Bouton triage T7x ---
        if button_id.startswith('triage-btn-'):
            triage_key = button_id[len('triage-btn-'):]
            nb = len(triage_data.get(triage_key, []))
            for i, (aig_id, target_devie) in enumerate(triage_data[triage_key]):
                if target_devie is None:
                    target_devie = not current_state.get(aig_id, False)
                current_state[aig_id] = target_devie
                _pulse_aig(aig_id, target_devie)
                if i < nb - 1:
                    time.sleep(INTER_PULSE_DELAY)
            info = f"Route {triage_key} activée ({nb} aiguillages)"

        # --- Bouton aiguillage individuel ---
        else:
            if button_id.startswith('state-btn-'):
                aiguillage_id = button_id[len('state-btn-'):]
            else:
                aiguillage_id = button_id[len('btn-'):]
            current_state[aiguillage_id] = not current_state[aiguillage_id]
            devie = current_state[aiguillage_id]
            _pulse_aig(aiguillage_id, devie)
            info = f"Aiguillage {aiguillage_id} → {'dévié' if devie else 'droit'}"

        images, btn_children, btn_styles = _build_outputs()
        return images + btn_children + btn_styles + [current_state, info]
