import json
from flask import Flask, render_template, request, jsonify
from markupsafe import escape
import functions_framework
import stationapi

app = Flask(__name__)

@app.route('/')
def index():
    return hello_http(request)

@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        name = "World"
    res_dict = dict(
        testmsg=f"Hello {escape(name)}!"
    )
    station_list_str = request.args.get('station_list_str', default = '立川、新宿', type = str)
    res_dict.update(stationapi.find_center_station(station_list_str))
    response = jsonify(res_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True)