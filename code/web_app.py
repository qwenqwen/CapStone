import pandas as pd
import cPickle as pickle
from flask import Flask, request, render_template
app = Flask(__name__)

# home page
@app.route('/')
def index():
    return render_template("index.html")


# My model prediction app
@app.route('/printout', methods=['GET', 'POST'] )
def printout():
    entered_time = str(request.form['time_limit'])
    recipe_name = 'ASDFGHJKL'
    ori_link = 'https://github.com/qwenqwen/CapStone'
    cooking_time = 30
    ingredients = ['aaa', 'bbb']
    procedures = 'asdfqwer'
    return render_template("printout.html", name = recipe_name, link = ori_link, \
        time = cooking_time, ingreds = ingredients, proc = procedures)
    '''with open('data/vectorizer.pkl') as f:
        vectorizer = pickle.load(f)
    with open('data/model.pkl') as f:
        model = pickle.load(f)

    text = str(request.form['user_input'])
    df = pd.read_csv(text)
    X = vectorizer.transform(df['body'])
    y = df['section_name']
    page = 'Accuracy: {0} <br><br>Predictions: {1}<br>'
    return page.format(model.score(X, y), model.predict(X))'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True)
