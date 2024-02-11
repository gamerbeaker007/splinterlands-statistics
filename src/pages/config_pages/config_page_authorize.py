import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, dcc, ctx, State
from dash import html

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_layout():
    layout = dbc.Row([
        html.H3('Add posting key for account:', className='mt-5'),
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText('Account'),
                dcc.Dropdown(id=config_page_ids.posting_key_user_dropdown,
                             options=store_util.get_account_names(),
                             className='dbc',
                             style={"width": "70%"},
                             ),
            ], className='mb-3'),
            width=4
        ),
        dbc.Col(
            dbc.Input(id=config_page_ids.posting_key_input,
                      type='text',
                      placeholder='hive posting key',
                      className='m-1 border border-dark',
                      ),
            className='dbc',
            width=3
        ),
        dbc.Col(
            dbc.Button('Update',
                       id=config_page_ids.add_posting_key_button,
                       className='m-1',
                       ),
            width=1
        ),
        html.Div(id=config_page_ids.posting_key_text, className='mb-3'),

    ]),
    return layout


@app.callback(
    Output(config_page_ids.posting_key_user_dropdown, 'value'),
    Output(config_page_ids.posting_key_user_dropdown, 'options'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
)
@measure_duration
def update_posting_key_user_list(added_trigger, removed_trigger):
    return store_util.get_first_account_name(), store_util.get_account_names()


@app.callback(
    Output(config_page_ids.account_updated, 'data'),
    Output(config_page_ids.posting_key_text, 'children'),
    Input(config_page_ids.add_posting_key_button, 'n_clicks'),
    State(config_page_ids.posting_key_user_dropdown, 'value'),
    State(config_page_ids.posting_key_input, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def update_posting_key(n_clicks, username, posting_key):
    if config_page_ids.add_posting_key_button == ctx.triggered_id:
        updated = False
        if not config.read_only:
            if not username:
                text = 'Select username, or first add username'
                class_name = 'text-warning'
            else:
                if not posting_key:
                    text = 'Missing posting key '
                    class_name = 'text-warning'
                else:
                    try:
                        token, version = spl.get_token(username, posting_key)
                        data = [[username, version, token]]
                        df = pd.DataFrame(data, columns=['username', 'version', 'token'])
                        store.secrets = pd.concat([store.secrets, df], ignore_index=True)
                        store_util.save_single_store('secrets')
                        text = 'Token Stored'
                        class_name = 'text-success'
                        updated = True
                    except (AssertionError, ValueError):
                        text = 'Invalid username / posting key combination'
                        class_name = 'text-danger'

        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

        return updated, html.Div(text, className=class_name)
