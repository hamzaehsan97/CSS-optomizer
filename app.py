from flask.globals import request
from optomize.main import Optomize
from flask import Flask
import os
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return("hello")


@app.route("/optomize", methods=['GET', 'POST'])
def optomize():
    try:
        html_url = request.args.get('html_url')
        css_url = request.args.get('css_url')
        html_url = str(html_url)
        css_url = str(css_url)
        opt = Optomize(html_url, css_url)
        results = opt.run()
        del opt
        return(results)
    except Exception as e:
        print(e)
        return{"error: ": e}

