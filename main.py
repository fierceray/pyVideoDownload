from flask import Flask, request, render_template, redirect
import os.path

import requests

CHUNK_SIZE = 256



application = Flask(__name__)

@application.route('/', methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        url = request.form.get('input_url')
        print(url)
        print(os.path.exists('/media'))
    return render_template("index.html")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    application.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
