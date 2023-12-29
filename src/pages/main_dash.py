from dash_bootstrap_templates import load_figure_template
from dash_extensions.enrich import LogTransform, TriggerTransform, DashProxy, NoOutputTransform

from src.configuration import config

dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'
load_figure_template([config.dark_theme, config.light_theme])

app = DashProxy(
    assets_folder='./assets',
    transforms=[
        TriggerTransform(),
        LogTransform(),
        # MultiplexerTransform(),
        NoOutputTransform(),
        # CycleBreakerTransform(),
        # BlockingCallbackTransform(),
        # ServersideOutputTransform(),
    ],
    external_stylesheets=[dbc_css, 'styles.css'],
    # meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
    suppress_callback_exceptions=True,
    title="Splinterlands - statistics",
    update_title=None
)
