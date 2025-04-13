from dash import register_page, html, dcc

register_page(__name__, path="/", name="Game Analysis")

layout = html.Div([
    html.H2("Welcome!  Click a link in the header to get started"),
    html.Img(
        src="/assets/dashboard.jpg",
        alt="Futuristic Dashboard Demo",
        style={
            "width": "100%",
            "max-width": "800px",  # Limit max width for larger screens
            "height": "auto",      # Maintain aspect ratio
            "margin-top": "20px",  # Space above the image
            "border-radius": "10px",  # Rounded corners
            "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"  # Subtle shadow for depth
        }
    )
])
