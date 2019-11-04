from flask import render_template
import datetime
from pytz import timezone

# assumption made for course purposes that we only use this for now in Texas
dt_central = timezone('US/Central')


def convert(model_obj):
    if isinstance(model_obj, list):
        result = []
        for obj in model_obj:
            result.append(convert(obj))
        return result

    dict_row = model_obj.__dict__
    result = {}

    for key, value in dict_row.items():
        if value is None:
            continue
        elif key in []:
            new_value = []
            for val in value:
                new_value.append(convert(val))
            result[key] = new_value
        elif key in ['giftable', 'redeemable']:
            result[key] = convert(value)
        elif isinstance(value, datetime.datetime):
            result[key] = value.astimezone(dt_central).strftime('%c')
        elif key not in ['_sa_instance_state']:
            result[key] = value

    return result


def delay(route: str, flags: list, js=None):
    def invoke(new_flags: list, data=None):
        args = {} if data is None else {'data': data}
        if js is not None:
            args['js'] = js
        for flag in flags + new_flags:
            args[flag] = True
        return render_template(route, **args)

    return invoke
