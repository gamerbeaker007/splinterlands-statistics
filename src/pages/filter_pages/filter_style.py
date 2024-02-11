def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False


def determine_class(active):
    if active:
        class_name = 'dbc bg-opacity-30 bg-danger'
    else:
        class_name = 'dbc bg-opacity-10 bg-dark'
    return class_name
