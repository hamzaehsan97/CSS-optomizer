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
        url = request.args.get('html_url')
        cwd = os.getcwd()
        html_path = str(url)
        css_path ="/optomize/files/styling.css"
        opt = Optomize(html_path, css_path)
        results = opt.run()
        del opt
        return(results)
    except Exception as e:
        print(e)
        return{"error: ": e}

