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
As the result, now I have a data frame with all features that I can use for modeling.

### Modeling

### Prediction
