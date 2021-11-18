import os
import math
import json
from flask import jsonify
from config.settings import BASEDIR


def render_json(status, *args, **kwargs):
    """
    Return a JSON response.

    Example usage:
      render_json(404, {'error': 'Discount code not found.'})
      render_json(200, {'data': coupon.to_json()})

    :param status: HTTP status code
    :type status: int
    :param args:
    :param kwargs:
    :return: Flask response
    """
    response = jsonify(*args, **kwargs)
    response.status_code = status

    return response


def convert_None_to_empty_string(data):
    for k, v in data.items():
        if (
          v == None 
          or (type(v) == float and math.isnan(v))
        ): 
            data[k] = ""
    return data

def write_to_file(file_name, data):
    json_path = os.path.join(BASEDIR, "documents", f"{file_name}.json")
    with open(json_path, 'w') as f:
        json.dump(data, f)

def read_from_file(file_name):
    json_path = os.path.join(BASEDIR, "documents", f"{file_name}.json")
    with open(json_path, 'r+') as f:
        data = json.load(f)
    return data

