import os
import sys

from dash_bootstrap_templates import load_figure_template
from dash_extensions.enrich import TriggerTransform, DashProxy, \
    NoOutputTransform, LogTransform, MultiplexerTransform, BlockingCallbackTransform, CycleBreakerTransform

from src.configuration import config

dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.1.1/dbc.min.css'
load_figure_template([config.dark_theme, config.light_theme])

if getattr(sys, 'frozen', False):
    assets_folder = os.path.join(sys._MEIPASS, 'assets')
else:
    assets_folder = os.path.join(os.getcwd(), 'assets')

app = DashProxy(
    __name__,
    assets_folder=assets_folder,
    transforms=[
        TriggerTransform(),
        LogTransform(),
        MultiplexerTransform(),
        NoOutputTransform(),
        CycleBreakerTransform(),
        BlockingCallbackTransform(),
        # ServersideOutputTransform(),
    ],
    external_stylesheets=[dbc_css, 'styles.css'],
    # meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}],
    suppress_callback_exceptions=True,
    title="Splinterlands - statistics",
    update_title=None
)
