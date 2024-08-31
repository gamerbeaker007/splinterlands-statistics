import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, State, dcc, html, MATCH, ctx, ALL
from dash.exceptions import PreventUpdate

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.pages.shared_modules import styles
from src.static import static_values_enum
from src.utils import store_util
from src.utils.trace_logging import measure_duration

layout = html.P('Loading data....')


def generate_account_buttons(accounts):
    buttons = []
    for account in accounts:
        buttons.append(
            html.Div(
                children=[
                    html.Img(
                        src=static_values_enum.helm_icon_url,
                        className='m-1'
                    ),
                    html.Label(
                        account,
                        id={'type': 'label', 'index': account},
                        # id=f'{account}_input',
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
                        id={'type': 'dynamic-button', 'index': account},  # Use pattern-matching ID
                        color="primary",
                        style=styles.get_read_only_mode_style(),
                        className='m-1'
                    ),
                    html.P(
                        id={'type': 'status-field', 'index': account},
                        style={'display': 'inline-block'},
                        className='m-1')
                ],
                className='dbc',
            )
        )
    return buttons


@app.callback(
    Output(config_page_ids.authorize_place_holder, 'children'),  # Update this to your main layout's ID
    Output(config_page_ids.account_updated, 'data'),  # Update this to your main layout's ID
    Input(config_page_ids.account_added, 'data'),  # Trigger the layout update when account data is updated
    Input(config_page_ids.account_removed, 'data'),  # Trigger the layout update when account data is updated
)
def update_layout(added, removed):
    accounts = store_util.get_account_names()
    account_buttons = generate_account_buttons(accounts)

    new_layout = dbc.Row([
        html.Div(
            children=account_buttons,
            className='dbc',
        ),
        html.Div(id=config_page_ids.posting_key_text, className='mb-3'),
        dcc.Store(id=config_page_ids.token_message_store),
    ])
    return new_layout, True


# Client-side callback to handle Hive Keychain signing and storing the encoded message
app.clientside_callback(
    """
    function(n_clicks, button_ids) {
        console.log(n_clicks)
        console.log(button_ids)
        
        if (n_clicks) {
            const clicked_button_id = n_clicks.findIndex(click => click > 0);
            const username = button_ids[clicked_button_id].index;
            
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
    Input({'type': 'dynamic-button', 'index': ALL}, 'n_clicks'),  # Updated Input
    State({'type': 'dynamic-button', 'index': ALL}, 'id'),  # Updated State
    prevent_initial_call=True,
)


@app.callback(
    Output(config_page_ids.posting_key_text, 'children'),
    Output(config_page_ids.account_updated, 'data'),
    Input(config_page_ids.token_message_store, 'data'),
    State({'type': 'dynamic-button', 'index': ALL}, 'n_clicks'),  # Updated Input

    prevent_initial_call=True,
)
@measure_duration
def store_new_management_account(data, n_clicks):
    if not any(n_clicks):
        raise PreventUpdate

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
            text = 'Unsuccessful sign message with hive'
            class_name = 'text-danger'
    else:
        text = 'This is not allowed in read-only mode'
        class_name = 'text-danger'

    return html.Div(text, className=class_name), updated


@app.callback(
    Output({'type': 'status-field', 'index': MATCH}, 'children'),
    Output({'type': 'status-field', 'index': MATCH}, 'className'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
    Input(config_page_ids.account_updated, 'data'),
    State({'type': 'label', 'index': MATCH}, 'children'),  # Assuming input field is of type 'dynamic-input'
)
@measure_duration
def update_status_field(added, removed, updated, username):
    if not ctx.triggered_id:
        raise PreventUpdate
    print('trigger:' + str(ctx.triggered_id) + ' for: ' + str(username))
    if ctx.triggered_id and username:
        token_dict = store_util.get_token_dict(username)
        if spl.verify_token(token_dict):
            children = [
                html.I(className='m-1 fas fa-check-circle'),
                f'Connected to Splinterlands API'
            ]
            color = 'text-success'
        else:
            children = [
                html.I(className='m-1 fas fa-exclamation-triangle'),
                'Not connected to Splinterlands API'
            ]
            color = 'text-warning'
    else:
        children = [
            html.I(className='m-1 fas fa-exclamation-triangle'),
            'Error connecting to Splinterlands API'
        ]
        color = 'text-danger'

    return children, color
