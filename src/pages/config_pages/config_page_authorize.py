import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, State, dcc
from dash import html

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.static import static_values_enum
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_layout():
    layout = dbc.Row([
        html.H3('Connect to splinterlands API:', className='mt-5'),
        html.P([
            'This account is used to communicate with the splinterlands API.',
            html.Br(),
            'If not connected not all function will be available',
            html.Br(),
            html.Br(),
            'Not connected functions:',
            html.Li('Portfolio (Portfolio/Land)'),
            html.Br(),
            'Connected functions: ',
            html.Li('Portfolio (Portfolio/Land)'),
            html.Li('Battle monitoring (Home/Losing/Card/Rating/Nemesis)'),
            html.Li('Season monitoring (Season/Hive blog generation)'),
        ]),
        dbc.Col(
            html.Div(
                children=[
                    html.Img(
                        src=static_values_enum.helm_icon_url,
                        className='m-1'
                    ),
                    dcc.Input(
                        type="text",
                        placeholder="Username",
                        id=config_page_ids.management_account_input,
                        className='m-1 p-1 border border-dark',
                        style={"width": "20%"},
                    ),
                    dbc.Button(
                        children=[
                            html.Span("CONNECT WITH"),
                            html.Img(
                                src=static_values_enum.hive_keychain_logo,
                            )
                        ],
                        id=config_page_ids.connect_management_account_button,
                        color="primary",
                        className='m-1'
                    ),
                ],
                className='dbc',
            ),
        ),
        html.Div(id=config_page_ids.posting_key_text, className='mb-3'),

        dcc.Store(id=config_page_ids.token_message_store),

    ]),
    return layout


# Client-side callback to handle Hive Keychain signing and storing the encoded message
app.clientside_callback(
    """
    function(n_clicks, username) {
        if (n_clicks > 0) {
            // Check if hive_keychain is available
            if (typeof window.hive_keychain === 'undefined') {
                console.error('Hive Keychain SDK not found!');
                return {
                    "success": false,
                    "message": "Hive Keychain SDK not loaded.",
                    "username": username,
                    "ts": null,
                    "sig": null
                };
            }

            // Now attempt to use the SDK
            const keychain = window.hive_keychain;
            const ts = Date.now();
            const message = username + ts;

            return new Promise((resolve) => {
                keychain.requestSignBuffer(username, message, 'Posting', (response) => {
                    console.log(response);
                    if (response.success) {
                        const encodedMessage = response.result;
                        resolve({
                            "success": true,
                            "message": "Message signed successfully!",
                            "username": username,
                            "ts": ts,
                            "sig": encodedMessage
                        });
                    } else {
                        console.error('Error in response:', response.error);
                        resolve({
                            "success": false,
                            "message": "Error in signing message.",
                            "username": username,
                            "ts": ts,
                            "sig": null
                        });
                    }
                });
            });
        }
        return {
            "success": false,
            "message": "No clicks detected.",
            "username": null,
            "ts": null,
            "sig": null
        };
    }
    """,
    Output(config_page_ids.token_message_store, 'data'),
    Input(config_page_ids.connect_management_account_button, 'n_clicks'),
    State(config_page_ids.management_account_input, 'value'),
    prevent_initial_call=True,
)


@app.callback(
    Output(config_page_ids.posting_key_text, 'children'),
    Output(config_page_ids.account_updated, 'data'),
    Input(config_page_ids.token_message_store, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def store_new_management_account(data):
    if not config.read_only:
        if data and data.get('success'):
            username = data['username']
            if not username:
                text = 'Select username, or first add username'
                class_name = 'text-warning'
            else:
                ts = data['ts']
                sig = data['sig']
                token, timestamp = spl.get_token(username, ts, sig)
                data = [[username, timestamp, token]]
                store.secrets = pd.DataFrame(data, columns=['username', 'timestamp', 'token'])
                store_util.save_stores()
                text = ''
                class_name = 'text-success'
        else:
            text = 'Unsuccessful sing message with hive '
            class_name = 'text-danger'
    else:
        text = 'This is not allowed in read-only mode'
        class_name = 'text-danger'

    return html.Div(text, className=class_name), True
