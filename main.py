from flask import Flask, render_template
from data import db_session
import json


with open('data/actual_events.json', encoding='utf-8') as events:
    f = events.read()
    afisha_data = json.loads(f)

with open('data/news_articles.json', encoding='utf-8') as na:
    f1 = na.read()
    NA = json.loads(f1)

with open('data/concerts.json', encoding='utf-8') as conc:
    f = conc.read()
    concerts = json.loads(f)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           afisha=afisha_data,
                           news=NA)

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/archive')
def archive():
    return render_template('archive.html', concerts=concerts)

@app.route('/actual_events')
def actual_events():
    return render_template('actual_events.html')

db_session.global_init("db/users.db")
db_session.global_init("db/posts.db")

if __name__ == '__main__':
    app.run(port=8080,  host='127.0.0.1')