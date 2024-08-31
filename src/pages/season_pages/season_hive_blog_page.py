import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx, dcc, State
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Trigger

from src.configuration import store, progress, config
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids, season_status
from src.utils import store_util, season_util
from src.utils.trace_logging import measure_duration


def get_readonly_style():
    if config.read_only:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def get_readonly_text():
    if config.read_only:
        return html.P('Read only mode... Not possible to generate blog.', className='text-warning')
    return ''


layout = dbc.Accordion(
    dbc.AccordionItem([
        dbc.Row(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Accounts'),
                    dcc.Dropdown(
                        multi=True,
                        id=season_ids.dropdown_user_selection_season_blog,
                        className='dbc',
                    ),
                ], className='mb-3',
            ),
        ),
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    'Generate',
                    id=season_ids.generate_blog_button,
                    className='mb-3'),
                style=get_readonly_style(),
                width='auto'),
            dbc.Col(html.Div(id=season_ids.clipboard_div,
                             style={'display': 'none'},
                             children=dcc.Clipboard(id=season_ids.copy_to_clipboard, style={'fontSize': 25})
                             ),
                    )

        ]),
        dbc.Row([
            html.Div(id=season_ids.error_hive_blog, children=get_readonly_text()),
            html.Div(id=season_ids.text_output_temp)
        ]),
    ], title='Generate last season blog',
    ),
    start_collapsed=True,
),


@app.callback(
    Output(season_ids.error_hive_blog, 'children'),
    Input(season_ids.generate_blog_button, 'n_clicks'),
    State(season_ids.dropdown_user_selection_season_blog, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def generate_hive_blog(n_clicks, users):
    message = [html.P(html.Div('', className='text-warning'))]
    if season_ids.generate_blog_button == ctx.triggered_id:
        if config.read_only:
            return [html.P(html.Div('This is not allowed in read-only mode', className='text-danger'))]

        for account in users:
            if not store_util.get_token_dict(account):
                return [
                    html.P(html.Div('Not connected to splinterlands API abort generation', className='text-danger'))]

        if users:
            previous_season_id = store.season_end_dates.id.max() - 1
            sps_df = store_util.get_season_values(store.season_sps, previous_season_id, users)

            error = False
            missing_data_for_users = []
            for account in users:
                player_spd_df = sps_df.loc[sps_df.player == account]
                if player_spd_df.empty or not (player_spd_df.season_id == previous_season_id).all():
                    missing_data_for_users.append(account)
                    error = True

            if error:
                message = [
                    html.P([
                        'Latest season information is missing for accounts: ' + ', '.join(missing_data_for_users),
                        html.Br(),
                        'Check account connection in config page and update seasons first',
                    ],
                        className='text-warning')
                ]
            else:
                season_status.hive_blog_text = season_util.generate_season_hive_blog(previous_season_id, users)
                message = [html.P(html.Div('Generation finished ready to copy', className='text-success'))]
    else:
        message = [html.P(html.Div('No accounts selected', className='text-warning'))]

    return message


@app.callback(
    Output(season_ids.dropdown_user_selection_season_blog, 'value'),
    Output(season_ids.dropdown_user_selection_season_blog, 'options'),
    Trigger(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list():
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(
    Output(season_ids.generate_blog_button, 'disabled'),
    Output(season_ids.update_season_btn, 'disabled'),
    Input(season_ids.generate_blog_button, 'n_clicks'),
    Input(season_ids.update_season_btn, 'n_clicks'),
)
@measure_duration
def disable_buttons(n_clicks_generate_blog, n_clicks_update_season_btn):
    if not ctx.triggered_id:
        raise PreventUpdate

    return True, True


@app.callback(
    Output(season_ids.generate_blog_button, 'disabled'),
    Output(season_ids.update_season_btn, 'disabled'),
    Trigger(nav_ids.interval_global, 'n_intervals')
)
def check_button_status():
    if progress.progress_season_txt:
        return True, True
    else:
        generate_blog_disabled = False
        if store.season_sps.empty:
            generate_blog_disabled = True

        return generate_blog_disabled, False


@app.callback(
    Output(season_ids.clipboard_div, 'style'),
    Trigger(nav_ids.interval_global, 'n_intervals')
)
def check_clipboard_style():
    if not season_status.hive_blog_text:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@app.callback(
    Output(season_ids.copy_to_clipboard, 'content'),
    Output(season_ids.text_output_temp, 'children'),
    Input(season_ids.copy_to_clipboard, 'n_clicks'),
    prevent_initial_call=True,
)
@measure_duration
def update_copy_to_clipboard(n_clicks):
    if not ctx.triggered_id:
        raise PreventUpdate

    if ctx.triggered_id == season_ids.copy_to_clipboard:
        if season_status.hive_blog_text:
            return season_status.hive_blog_text, [html.P('Text is copied to clipboard')]
        else:
            return '', [html.P('Text is copied to clipboard')]
