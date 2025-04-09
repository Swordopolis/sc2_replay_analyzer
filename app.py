# imports
import sc2reader                    # Library for reading StarCraft II replays 
from dash import Dash, html, dcc, Input, Output, callback
import base64
import io

from functions import initialize_data_structures
from functions import parse_events

from plots import plot_collection_rates
from plots import plot_workers_active
from plots import plot_income_advantage
from plots import plot_resources_available
from plots import plot_army_value
from plots import plot_tech_value
from plots import plot_supply
from plots import plot_unit_supply


def main(replay_bytes):
    replay = sc2reader.load_replay(io.BytesIO(replay_bytes))
    # player_names = [player.name for player in replay.players]
    
    # Create the player data structures
    player_data = initialize_data_structures(replay)

    # Populate player data structures with event information
    player_data = parse_events(replay, player_data)  # unit_list from sc2_data

    figures = {
        "collection_rates": plot_collection_rates(player_data),
        "workers_active": plot_workers_active(player_data),
        "income_advantage": plot_income_advantage(player_data),
        "resources_available": plot_resources_available(player_data),
        "army_value": plot_army_value(player_data),
        "tech_value": plot_tech_value(player_data),
        "supply": plot_supply(player_data),
    }
    # Add unit supply graphs for each player
    for i, player_name in enumerate(player_data.keys()):
        figures[f"unit_supply_{i}"] = plot_unit_supply(player_data, player_name)

    return figures

# Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.H1("StarCraft II Replay Analyzer"),
    dcc.Upload(
        id="upload-replay",
        children=html.Button("Select Replay File"),
        multiple=False,
        accept=".SC2Replay"
    ),
    html.Div(id="graph-output", style={"max-height": "80vh", "overflow-y": "auto"})
], style={"font-family": "Arial, sans-serif"})

@callback(
    Output("graph-output", "children"),
    Input("upload-replay", "contents")
)

def update_graph(contents):
    if contents:
        try:
            content_type, content_string = contents.split(',')
            replay_bytes = base64.b64decode(content_string)
            figures = main(replay_bytes)
            graphs = [
                dcc.Graph(id="collection-rates-graph", figure=figures["collection_rates"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="workers-active-graph", figure=figures["workers_active"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="income-advantage-graph", figure=figures["income_advantage"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="resources-available-graph", figure=figures["resources_available"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="army-value-graph", figure=figures["army_value"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="tech-value-graph", figure=figures["tech_value"], style={"margin-bottom": "20px"}),
                dcc.Graph(id="supply-graph", figure=figures["supply"], style={"margin-bottom": "20px"}),
            ]
            # Add unit supply graphs dynamically
            for i in range(len(figures) - len(graphs)):  # Number of unit supply graphs
                graphs.append(
                    dcc.Graph(id=f"unit-supply-graph-{i}", figure=figures[f"unit_supply_{i}"], style={"margin-bottom": "20px"})
                )
            return html.Div(graphs, style={"width": "100%", "display": "flex", "flex-direction": "column"})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return html.Div(f"Error: {str(e)}\n\nDetails:\n{error_details}", style={"white-space": "pre-wrap"})
    return html.Div("Upload a replay file to generate the graphs.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)