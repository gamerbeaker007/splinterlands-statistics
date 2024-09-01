import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, State, dcc, html

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.static import static_values_enum
from src.utils import store_util
from src.utils.trace_logging import measure_duration

layout = dbc.Row([
    dbc.Col(
        html.Img(
            src=static_values_enum.helm_icon_url,
            className='m-1 p-2'
        ),
        width="auto"
    ),
    dbc.Col(
        dcc.Dropdown(
            id=config_page_ids.account_dropdown,
            options=store_util.get_account_names(),
            value=store_util.get_first_account_name(),
            className='dbc m-1',
        ),
        width=3
    ),
    dbc.Col(
        dbc.Button(
            children=[
                html.Span("CONNECT WITH"),
                html.Img(
                    src=static_values_enum.hive_keychain_logo,
                )
            ],
            id=config_page_ids.connect_button,
            color="primary",
            className="m-1",
        ),
        width="auto"
    ),
    html.Div(id=config_page_ids.posting_key_text, className='mb-3'),
    html.Hr(),
    dcc.Store(id=config_page_ids.token_message_store),
]),

# Client-side callback to handle Hive Keychain signing and storing the encoded message
app.clientside_callback(
    """
    function(n_clicks, username) {
        if (n_clicks) {           
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
    Input(config_page_ids.connect_button, 'n_clicks'),
    State(config_page_ids.account_dropdown, 'value'),
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
    updated = False
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

                # Check if the username already exists in store.secrets
                if not store.secrets.empty and username in store.secrets['username'].values:
                    # Update the existing record
                    store.secrets.loc[
                        store.secrets['username'] == username, ['timestamp', 'token']
                    ] = [timestamp, token]
                else:
                    # Add a new record
                    new_data = pd.DataFrame([[username, timestamp, token]], columns=['username', 'timestamp', 'token'])
                    store.secrets = pd.concat([store.secrets, new_data], ignore_index=True)

                store_util.save_stores()
                updated = True
                text = ''
                class_name = 'text-success'

        else:
            text = 'Connect with hive keychain was unsuccessful'
            class_name = 'text-danger'
    else:
        text = 'This is not allowed in read-only mode'
        class_name = 'text-danger'

    return html.Div(text, className=class_name), updated


@app.callback(
    Output(config_page_ids.account_dropdown, 'value'),
    Output(config_page_ids.account_dropdown, 'options'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
    Input(config_page_ids.account_updated, 'data'),
)
@measure_duration
def update_user_list(added, removed, updated):
    return store_util.get_first_account_name(), store_util.get_account_names()
