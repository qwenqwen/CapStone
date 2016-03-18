import pandas as pd
import numpy as np
import cPickle as pickle
from flask import Flask, request, render_template, redirect
import string
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
    printable = set(string.printable)
    error_found = 0
    entered_time = str(request.form['time_limit'])
    entered_ing_yes = str(request.form['ing_yes'])
    entered_ing_no = str(request.form['ing_no'])
    # if the time entered is not a number
    if not is_number(entered_time):
        error_found = 1
        # error_message = 'Not a number!'
        return render_template("printout.html", err = error_found, all_info = [])
    # if the time entered is too short, a Google map is returned
    elif float(entered_time) < 5:
        return redirect('https://www.google.com/maps/preview#!q=restaurant')
    else:
        choices = list(df[df['estimated_time'] <= float(entered_time)].index)
        # apply filters
        if (entered_ing_yes and (not entered_ing_yes.isspace())):
            entered_ing_yes_split = [i.strip().lower() for i in entered_ing_yes.split(',')]
            # check if the ingredients are in the available recipes
            choices_yes = [i for i in choices if all(j in df['Ingredients'][i] for j in entered_ing_yes_split)]
            choices = choices_yes
        if (entered_ing_no and (not entered_ing_no.isspace())):
            entered_ing_no_split = [i.strip().lower() for i in entered_ing_no.split(',')]
            # check if the ingredients are not in the available recipes
            choices_no = [i for i in choices if all(j not in df['Ingredients'][i] for j in entered_ing_no_split)]
            choices = choices_no
        if len(choices) == 0:
            error_found = 2
            return render_template("printout.html", err = error_found, all_info = [])
        # sort the list by estimated cooking Time
        estimate = [df['estimated_time'][i] for i in choices]
        sorted_order = np.argsort(estimate)[::-1]
        sorted_choices = list(np.array(choices)[sorted_order])
        sorted_estimate = [df['estimated_time'][i] for i in sorted_choices]
        recipe_name = [filter(lambda x: x in printable, df['Name'][i]) for i in sorted_choices]
        ori_link = [df['URL'][i] for i in sorted_choices]
        cooking_time = [df['Time'][i] for i in sorted_choices]
        image = [df['img_link'][i] for i in sorted_choices]
        number_of_recipe = len(choices)
    # return render_template("printout.html", name = recipe_name, link = ori_link, \
    #     ctime = cooking_time, etime = estimate, err = error_found)
    return render_template("printout.html", err = error_found, nor = number_of_recipe, \
        all_info = list(zip(recipe_name,ori_link,cooking_time,sorted_estimate,image)))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True)
