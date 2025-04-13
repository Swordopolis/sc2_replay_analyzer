from dash import Dash, html, dcc, page_container

# Dash App
app = Dash(__name__, use_pages=True)  # Enable pages auto-discovery

# Main layout with header bar
app.layout = html.Div([
    html.H1("StarCraft II Replay Analyzer", style={"text-align": "center"}),
    html.Nav([
        dcc.Link("Game Analysis", href="/", style={
            "margin-right": "20px", "text-decoration": "none", "color": "#007bff", "font-size": "18px"
        }),
        dcc.Link("Game Comparison", href="/compare", style={
            "margin-right": "20px", "text-decoration": "none", "color": "#007bff", "font-size": "18px"
        })
    ], style={
        "background-color": "#f8f9fa", "padding": "10px", "margin-bottom": "20px", "border-bottom": "1px solid #dee2e6"
    }),
    page_container  # Renders page content
], style={"font-family": "Arial, sans-serif", "margin": "0 auto", "max-width": "1200px"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)