# pages/compare.py
import dash
from dash import html, dcc, callback, Input, Output, State
import sc2reader
import base64
import io
from tools.functions import process_replay

dash.register_page(__name__, path="/compare", name="Game Comparison")

layout = html.Div([
    html.H2("Compare Players Across Replays"),
    html.Div([
        html.Div(  # Wrapper to restrict click area
            dcc.Upload(
                id="reference-replay",
                children=html.Button("Select Reference Replay"),
                multiple=False,
                accept=".SC2Replay",
            ),
            style={"display": "inline-block", "margin-right": "20px"}
        ),
        html.Label(id="reference-label", children=""),
        dcc.Dropdown(id="player-1", placeholder="Select Player 1", style={"width": "300px"})
    ], style={"margin-bottom": "20px"}),
    html.Div([
        html.Div(  # Wrapper to restrict click area
            dcc.Upload(
                id="comparison-replay",
                children=html.Button("Select Comparison Replay"),
                multiple=False,
                accept=".SC2Replay",
            ),
            style={"display": "inline-block", "margin-right": "20px"}
        ),
        html.Label(id="comparison-label", children=""),
        dcc.Dropdown(id="player-2", placeholder="Select Player 2", style={"width": "300px"})
    ], style={"margin-bottom": "20px"}),
    html.Div(id="compare-output", style={"max-height": "80vh", "overflow-y": "auto"}),
    dcc.Store(id="reference-replay-data"),
    dcc.Store(id="comparison-replay-data")
])

@callback(
    Output("reference-label", "children"),
    Input("reference-replay", "filename")
)
def update_reference_label(filename):
    if filename:
        return f"{filename}"
    return ""

@callback(
    Output("comparison-label", "children"),
    Input("comparison-replay", "filename")
)
def update_comparison_label(filename):
    if filename:
        return f"{filename}"
    return ""

@callback(
    Output("player-1", "options"),
    Input("reference-replay", "contents")
)
def update_player_1_dropdown(contents):
    if not contents:
        return []
    try:
        content_type, content_string = contents.split(',')
        replay_bytes = base64.b64decode(content_string)
        replay = sc2reader.load_replay(io.BytesIO(replay_bytes))
        return [{"label": p.name, "value": p.name} for p in replay.players]
    except Exception:
        return []

@callback(
    Output("player-2", "options"),
    Input("comparison-replay", "contents")
)
def update_player_2_dropdown(contents):
    if not contents:
        return []
    try:
        content_type, content_string = contents.split(',')
        replay_bytes = base64.b64decode(content_string)
        replay = sc2reader.load_replay(io.BytesIO(replay_bytes))
        return [{"label": p.name, "value": p.name} for p in replay.players]
    except Exception:
        return []

@callback(
    [Output("compare-output", "children"),
     Output("reference-replay-data", "data"),
     Output("comparison-replay-data", "data")],
    [Input("reference-replay", "contents"),
     Input("comparison-replay", "contents"),
     Input("player-1", "value"),
     Input("player-2", "value")]
)

def compare_players(contents_1, contents_2, player_1, player_2):
    from tools.plots import (
        plot_collection_rates,
        plot_workers_active,
        plot_income_advantage,
        plot_resources_available,
        plot_army_value,
        plot_tech_value,
        plot_supply,
        plot_unit_supply
    )

    if not all([contents_1, contents_2, player_1, player_2]):
        return html.Div("Upload both replays and select players to compare."), None, None

    try:
        # Process Replay 1 (Reference)
        content_type, content_string = contents_1.split(',')
        replay_bytes_1 = base64.b64decode(content_string)
        player_data_1 = process_replay(replay_bytes_1)

        # Process Replay 2 (Comparison)
        content_type, content_string = contents_2.split(',')
        replay_bytes_2 = base64.b64decode(content_string)
        player_data_2 = process_replay(replay_bytes_2)

        # Validate selected players
        if player_1 not in player_data_1 or player_2 not in player_data_2:
            return html.Div("Selected players not found in replays."), None, None

        # Tag players with replay identifier
        tagged_player_1 = f"Reference - {player_1}"
        tagged_player_2 = f"Comparison - {player_2}"

        # Combine data with tagged player names
        compare_data = {
            tagged_player_1: player_data_1[player_1],
            tagged_player_2: player_data_2[player_2]
        }

        # Generate comparison graphs
        figures = {
            "collection_rates": plot_collection_rates(compare_data),
            "workers_active": plot_workers_active(compare_data),
            "income_advantage": plot_income_advantage(compare_data),
            "resources_available": plot_resources_available(compare_data),
            "army_value": plot_army_value(compare_data),
            "tech_value": plot_tech_value(compare_data),
            "supply": plot_supply(compare_data),
            f"unit_supply_0": plot_unit_supply(compare_data, tagged_player_1),
            f"unit_supply_1": plot_unit_supply(compare_data, tagged_player_2)
        }

        graphs = [
            dcc.Graph(id="compare-collection-rates", figure=figures["collection_rates"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-workers-active", figure=figures["workers_active"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-income-advantage", figure=figures["income_advantage"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-resources-available", figure=figures["resources_available"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-army-value", figure=figures["army_value"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-tech-value", figure=figures["tech_value"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-supply", figure=figures["supply"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-unit-supply-0", figure=figures["unit_supply_0"], style={"margin-bottom": "20px"}),
            dcc.Graph(id="compare-unit-supply-1", figure=figures["unit_supply_1"], style={"margin-bottom": "20px"})
        ]

        return html.Div(graphs, style={"width": "100%", "display": "flex", "flex-direction": "column"}), player_data_1, player_data_2
    except Exception as e:
        return html.Div(f"Error: {str(e)}"), None, None