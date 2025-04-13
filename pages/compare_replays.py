from dash import register_page, html, dcc, callback, Input, Output

register_page(__name__, path="/compare", name="Game Comparison")

layout = html.Div([
    html.H2("Compare Players Across Replays"),
    html.Div([
        html.Label("Replay 1:"),
        dcc.Upload(
            id="upload-replay-1",
            children=html.Button("Select Replay 1"),
            multiple=False,
            accept=".SC2Replay",
            style={"margin-right": "20px"}
        ),
        dcc.Dropdown(id="player-1", placeholder="Select Player 1", style={"width": "300px"})
    ], style={"margin-bottom": "20px"}),
    html.Div([
        html.Label("Replay 2:"),
        dcc.Upload(
            id="upload-replay-2",
            children=html.Button("Select Replay 2"),
            multiple=False,
            accept=".SC2Replay",
            style={"margin-right": "20px"}
        ),
        dcc.Dropdown(id="player-2", placeholder="Select Player 2", style={"width": "300px"})
    ], style={"margin-bottom": "20px"}),
    html.Button("Compare Players", id="compare-button", n_clicks=0),
    html.Div(id="compare-output", style={"max-height": "80vh", "overflow-y": "auto"}),
    dcc.Store(id="replay-data-1"),
    dcc.Store(id="replay-data-2")
])

@callback(
    Output("player-1", "options"),
    Input("upload-replay-1", "contents")
)
def update_player_1_dropdown(contents):
    if not contents:
        return []
    try:
        import sc2reader
        import base64
        import io
        content_type, content_string = contents.split(',')
        replay_bytes = base64.b64decode(content_string)
        replay = sc2reader.load_replay(io.BytesIO(replay_bytes))
        return [{"label": p.name, "value": p.name} for p in replay.players]
    except Exception:
        return []

@callback(
    Output("player-2", "options"),
    Input("upload-replay-2", "contents")
)
def update_player_2_dropdown(contents):
    if not contents:
        return []
    try:
        import sc2reader
        import base64
        import io
        content_type, content_string = contents.split(',')
        replay_bytes = base64.b64decode(content_string)
        replay = sc2reader.load_replay(io.BytesIO(replay_bytes))
        return [{"label": p.name, "value": p.name} for p in replay.players]
    except Exception:
        return []

@callback(
    Output("compare-output", "children"),
    [Input("compare-button", "n_clicks"),
     Input("upload-replay-1", "contents"),
     Input("upload-replay-2", "contents"),
     Input("player-1", "value"),
     Input("player-2", "value")]
)

def compare_players(n_clicks, contents_1, contents_2, player_1, player_2):
    if n_clicks == 0 or not all([contents_1, contents_2, player_1, player_2]):
        return html.Div("Upload both replays and select players to compare.")
    return html.Div("Comparison not implemented yet.")