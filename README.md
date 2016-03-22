# CapStone - WhatToEat

My CapStone Project about recipe time estimation

## Abstract

In this project, I built a recipe recommendation system that automatically extracts key words from online recipes and tried to estimate the time cost for the recipes, so that the system can recommend to the user a recipe that meets the user’s time constraint. Also, since the key words were collected from the recipe, the user can filter the selections by choosing cuisine type, dish type, absent / provided ingredients, and so on. A web app was created for test and illustration purpose.

## Motivation

The motivation was from my own experience. After I came to the bootcamp, the common time when I left Galvanize was after 6:30 PM. And I also need to take 45-minute bus ride to go back to the place I live. So I usually arrived at home at around 8 PM, hungry and exhausted. I didn’t want to spend too much time cooking, and there were not too many ingredients left in the refrigerator. So it was difficult to figure out something I like and won’t cost me too much time to prepare.
Most of the online recipes do not have a time estimate. People usually need do the estimation based on their experience. I am going to create a model to predict the time giving a recipe, and recommend one recipe that costs less time than the user-specified time limit.

## Procedure

As all data science projects, the general procedures are data acquisition, data cleaning, feature engineering, modeling, and prediction.

### Data Acquisition

There are a lot of recipe websites, but few of them provide recipes with time. For training purpose, I need recipes with time, so I stick to New York Times Cooking website, where many recipes are timed. The first round of scrapping was focused on "easy" recipes, with request intervals being set to a random number between 2 and 4.
HTML files were parsed using BeautifulSoup. And the useful information was saved in a data frame
For the search results,
1. Recipe time strings were extracted.
2. Recipe titles, IDs, URLs were extracted.

For each recipe, its URL was used to extract recipe information.
1. Ingredients were extracted.
2. Cooking procedure descriptions were extracted and saved a string.
3. Both ingredients and procedure descriptions were added to the data frame.

Now, I created the data frame with all useful information.

### Data Cleaning

For the information of recipe cooking time, I tried to get a value from the strings like "1 hour 15 minutes" or "15 to 30 minutes". Regular expressions were used to get the number before "hour/hours" and "minute/minutes". For the latter case, the first number (minimal time) was extracted. As the result, the "Time" column in the data frame contains the values in minutes.
For the information of ingredients, most of them are strings of ingredient names, but some of them are unstructured, which were long sentences. I had to extract ingredients from those sentences. The method is simple. First, a vocabulary set of all ingredients with short names (no more than 2 words) was created. Then, for each ingredient with long name (more than 2 words), it's checked to see if it contained any of the ingredients in the vocabulary. If there was any new ingredients, they were added to the ingredient list. As the result, the "Ingredients" column contains only ingredient names.
All non-ascii characters and parentheses including the contents inside were removed from the ingredient strings and procedure strings.

### Feature Engineering

The features for this project are the key words. Part of them are the ingredients, and another part are the verbs from the procedure descriptions. Python package textblob was used to tokenize and tag the words from the descriptions. Verbs were extracted and stemmized. Ingredients were split into single word and stemmized. There were also some missing words that were not captured by textblob. All these were used to create the vocabulary of key words.
Then the tf-idf values were calculated for all words in the vocabulary. And the values were added to the data frame as new features.
As the result, I had a data frame with all features that I can use for modeling.

### Modeling

Since this is a regression problem, multiple regression models were tried and compared based on r-squared error using cross-validation.
The recipes with given time can be used as training set. Since cross-validation was used in model selection, there is no need to split the training set. Additionally, only the recipes whose cooking time is less than 2 hours were used in the training set, since accuracy is more critical for simpler recipes.
Among all five models (linear regression, ada boosting, gradient boosting, random forest, and support vector machine), gradient boosting and random forest had much higher r-squared error scores. Then, residual plots were used to visually determine the performance difference. And as the result, random forest was selected to perform the prediction. But grid search is needed in the future to finally determine if gradient boosting can outperform random forest.

### Prediction

After the model was trained, the predictions were given to the complete data set.

## Web_app

As the final step, a convenient web-app was created for the users. From the app, users can enter the time limit, as well as the ingredient they do or do not want. The final results will be filtered accordingly.
The results will be sorted by estimated cooking time in descending order, with the given time (if any) next to the estimated time. And, if a picture is provided, it will be displayed.
If a recipe is selected, by clicking on the name, the users will be re-directed to the original recipe page for more details.
And, an Easter egg is there. Try to ignore the warning at the bottom of the front page and enter some numbers that are less than 5 ...

## Future work

One thing I do want to implement but not is to use the quantity of the ingredients. For example, 1 pound of beef may cost different time than 5 pounds of beef. But the difficulty is that the ingredients use different units and its hard to interpret and convert the units.

TextBlob is sometimes not good at labeling some verbs. Therefore, a better tagger is needed.

Last but not least, a prettier app is always a better thing.
