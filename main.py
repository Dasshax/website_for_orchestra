from flask import Flask, render_template
import json

with open('data/actual_events.json', encoding='utf-8') as events:
    f = events.read()
    afisha_data = json.loads(f)

with open('data/news_articles.json', encoding='utf-8') as na:
    f1 = na.read()
    NA = json.loads(f1)

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

if __name__ == '__main__':
    app.run(port=8080,  host='127.0.0.1')