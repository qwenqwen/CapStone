import pandas as pd
import cPickle as pickle
from flask import Flask, request, render_template
import random
app = Flask(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# home page
@app.route('/')
def index():
    return render_template("index.html")


# My model prediction app
@app.route('/printout', methods=['GET', 'POST'] )
def printout():
    with open('../data/df_final.pkl', 'rb') as f:
        df = pickle.load(f)
    entered_time = str(request.form['time_limit'])
    if not is_number(entered_time):
        recipe_name = 'Not a number!'
        ori_link = ''
        cooking_time = None
        ingredients = []
        procedures = ''
    elif float(entered_time) < 10:
        pass
    else:
        choices = list(df[df['estimated_time'] <= 20].index)
        pick = df.iloc[random.choice(choices),:]
        recipe_name = pick['Name']
        ori_link = pick['URL']
        cooking_time = pick['Time']
        ingredients = pick['Ingredients']
        procedures = pick['steps']
        estimate = pick['estimated_time']
    return render_template("printout.html", name = recipe_name, link = ori_link, \
        ctime = cooking_time, etime = estimate, ingreds = ingredients, proc = procedures)
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
