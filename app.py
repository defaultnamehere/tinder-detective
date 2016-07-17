
import requests

from flask import Flask, render_template, send_file

import api

app = Flask('tinder-detective')

stalker = api.NSASimulator()

@app.route('/')
def index():
    profiles = stalker.get_profiles()
    return render_template("main.html", profiles=profiles)


if __name__ == '__main__':
    app.run(debug=True)
