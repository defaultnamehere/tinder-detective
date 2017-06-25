

from flask import Flask, render_template, request

import api

app = Flask('tinder-detective')

stalker = api.NSASimulator()

@app.route('/')
def index():
    profiles = stalker.get_profiles()
    return render_template("main.html", profiles=profiles)

@app.route('/like/')
def like():
    user = request.args.get('user')
    stalker.like(user)
    return ''

@app.route('/superlike/')
def superlike():
    user = request.args.get('user')
    stalker.superlike(user)
    return ''

@app.route('/pass/')
def pass_vote():
    user = request.args.get('user')
    stalker.pass_vote(user)
    return ''

if __name__ == '__main__':
    app.run(debug=True)
