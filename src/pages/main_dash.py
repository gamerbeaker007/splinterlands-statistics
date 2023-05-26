import dash_bootstrap_components as dbc
from dash import Dash
from dash_bootstrap_templates import load_figure_template
from src.configuration import config

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template([config.dark_theme, config.light_theme])

app = Dash(__name__,
           external_stylesheets=[dbc.themes.CYBORG, dbc_css],
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True
           )

