from dash import register_page, html, dcc, callback, Input, Output
import base64
from tools.functions import main  # Import main from app.py

register_page(__name__, path="/", name="Game Analysis")

layout = html.Div([
    dcc.Upload(
        id="upload-replay",
        children=html.Button("Select Replay File"),
        multiple=False,
        accept=".SC2Replay"
    ),
    html.Div(id="graph-output", style={"max-height": "80vh", "overflow-y": "auto"})
])

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
            for i in range(len(figures) - len(graphs)):
                graphs.append(
                    dcc.Graph(id=f"unit-supply-graph-{i}", figure=figures[f"unit_supply_{i}"], style={"margin-bottom": "20px"})
                )
            return html.Div(graphs, style={"width": "100%", "display": "flex", "flex-direction": "column"})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return html.Div(f"Error: {str(e)}\n\nDetails:\n{error_details}", style={"white-space": "pre-wrap"})
    return html.Div("Upload a replay file to generate the graphs.")

