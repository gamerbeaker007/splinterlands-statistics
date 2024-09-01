import dash_bootstrap_components as dbc
from dash import html

pre_msg = [
    'Your account(s) needs to be connected to the Splinterlands API.',
    html.Br(),
    'This is essential for full access to the Splinterlands statistics website.',
    html.Br(),
    'Without connecting, some functions will be limited.',
    html.Br(),
    html.Br(),
]

msg_limited_access = [
    'Limited Access (Not Connected):',
    html.Br(),
    html.Li('Portfolio features (Portfolio/Land)'),
]

msg_full_access = [
    'Full Access (Connected):',
    html.Br(),
    html.Li('Portfolio features (Portfolio/Land)'),
    html.Li('Battle features (Home/Losing/Card/Rating/Nemesis)'),
    html.Li('Season features (Season/Hive blog generation)'),
]

post_msg = [
    html.Br(),
    'To unlock the full functionality of this site,',
    ' please ensure that your account is connected to the Splinterlands API.'
]

layout = dbc.Row([
    html.H3('Connect to splinterlands API:', className='mt-2'),
    html.P(pre_msg),
    dbc.Row([
        dbc.Col(
            html.Div(
                children=msg_limited_access,
                className='text-left'
            ),
            width=6
        ),
        dbc.Col(
            html.Div(
                children=msg_full_access,
                className='text-left'
            ),
            width=6
        )
    ]),
    html.P(post_msg),
])
