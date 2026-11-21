import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import components
import callbacks

# Fonction pour lire les positions depuis le fichier
def read_positions(filename):

    positions = {}
    with open(filename, 'r') as file:
        next(file)
        for line in file:
            data = line.strip().split(';')
            if len(data) >= 8:
                aiguillage_id = data[0]
                x = int(data[1])
                y = int(data[2])
                w = int(data[3])
                h = int(data[4])
                droit   = data[5]
                devie   = data[6]
                table   = data[7]
                inverse = bool(int(data[8])) if len(data) >= 9 else False
                positions[aiguillage_id] = {'x': x, 'y': y, 'w': w, 'h': h,
                                            'droit': droit, 'devie': devie,
                                            'table': table, 'inverse': inverse}
    return positions

def read_dashboard_data(filename):
    dashboard = {}
    with open(filename, 'r') as file:
        next(file)
        for line in file:
            data = line.strip().split(';')
            if len(data) == 3:
                aiguillage_id = data[0]
                i2c = data[1]
                spec = int(data[2])
                dashboard[aiguillage_id] = {'i2c': i2c, 'spec': spec}

    return dashboard


def read_triage_data(filename):
    triage = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(';')
                if len(parts) == 2:
                    key = parts[0].strip()
                    entries = []
                    for item in parts[1].split(','):
                        item = item.strip()
                        if ':' in item:
                            aig_id, state = item.split(':', 1)
                            entries.append((aig_id.strip(), state.strip() == 'v'))
                        elif item:
                            entries.append((item, None))  # None = toggle
                    triage[key] = entries
    except FileNotFoundError:
        print(f'Fichier {filename} introuvable, triage désactivé')
    return triage


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
positions      = read_positions('positions.txt')
dashboard_data = read_dashboard_data('positions mapping v2.txt')
triage_data    = read_triage_data('table_triage.txt')

if __name__ == '__main__':
    app.layout = components.layout(positions, dashboard_data, triage_data)
    callbacks.register_callbacks(app, positions, dashboard_data, triage_data)
    app.run(debug=True)
