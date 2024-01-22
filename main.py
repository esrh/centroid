from flask import Flask, render_template, request, jsonify
from markupsafe import escape
import functions_framework
import stationapi

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # テンプレートの自動リロードを有効にする
app.template_folder = '.'  # 新しいテンプレートフォルダのパスを設定

@app.route('/')
def index():
    return entry(request)

@app.route('/testpage/')
def testpage():
    return render_template('index.html')

@functions_framework.http
def entry(request):
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
    
    res_dict.update(stationapi.find_center_station(
        station_list_str=request.args.get('station_list_str', default = '立川、新宿', type = str),
        in_tokyo=True if request.args.get('in_tokyo', default = 'true', type = str) == 'true' else False
    ))
    response = jsonify(res_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
    response.headers.add("Pragma", "no-cache")
    response.headers.add("Expires", "0")
    return response

if __name__ == '__main__':
    app.run(debug=True)