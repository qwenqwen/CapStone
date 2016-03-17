import random, time, cPickle, string
import os.path
import pandas as pd
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from textblob import TextBlob

def NYT_easy_abstract():
    '''
    Scrape New York Times Cooking website for 'easy' recipes
    The BeautifulSoup objects are in a list, and each element in the list
    is a search page, containing multiple recipe abstracts.
    The list is saved in a pickle file for future use.
    '''
    all_soup = []
    for i in range(1,75):
        SLEEP_TIME = random.uniform(2,4)
        time.sleep(SLEEP_TIME)
        response = requests.get('http://cooking.nytimes.com/search?filters[meal_types][]=easy&q=&page=' + str(i))
        soup = BeautifulSoup(response.content, 'html.parser')
        all_soup.append(soup)
    with open('../data/easy_titles.pickle', 'w') as f:
        cPickle.dump(all_soup, f)
    return None

def extract_time(string):
    '''
    Extract time info from NYT Cooking recipes
    String format is like '1 hour 30 minutes', '15 minutes', '30 minutes to 1 hour'
    For a time range like '30 minutes to 1 hour', only the first part is extracted,
        but an indicator for time range is set to 1.
    Time is zero if there is not such information
    Return a tuple (time, time_range)
    '''
    time_range = 0 # indicator, 1 if the given time is a range
    hour = 0
    minute = 0
    given_time = 0
    before_to = string.split(' to ')[0] # string before "to". No change if there is no "to"
    if before_to != string: # The given time is a range
        time_range = 1
    # search for the digits before 'hour/hours' and 'minute/minutes'
    h = re.search('\d+ (?=hours*)', before_to)
    m = re.search('\d+ (?=minutes*)', before_to)
    if h is not None: # if 'hour/hours' exists in the string
        hour = int(h.group(0).strip())
    if m is not None: # if 'minute/minutes' exists in the string
        minute = int(m.group(0).strip())
    given_time = hour * 60 + minute
    return given_time, time_range

def NYT_easy_abstract_df():
    '''
    Unpickle the saved raw data and extract information from it
    The final result is saved in a data frame with 5 columns
    The data frame is pickled for future use.
    '''
    # unpickle the saved raw data
    with open('../data/easy_titles.pickle', 'r') as f:
        all_soup_unpickled = cPickle.load(f)
    # define an empty data frame for the abstract
    columns = ['Name','Time', 'Time_Range', 'ID', 'URL']
    df_NYT_abstract = pd.DataFrame(columns = columns)
    # extract information from each search page
    base_URL = 'http://cooking.nytimes.com'
    for i in xrange(len(all_soup_unpickled)):
        # get the lines with recipe information
        elements = all_soup_unpickled[i].findAll('a',href = re.compile("/recipes/"),class_="card-recipe-info")
        for ele in elements:
            one_row = []
            # d is in format of ['Seeded Pecan Granola', '  ', 'By The New York Times', '1 hour 15 minutes']
            d = ele.text.encode('utf8').strip().split('\n')
            # extract time
            time = extract_time(d[-1])
            one_row.extend([d[0], time[0], time[1]])
            # ele['href'].encode('utf8') is in format of '/recipes/1017997-seeded-pecan-granola'
            one_row.extend([ele['href'].encode('utf8').split('/')[-1].split('-')[0]])
            one_row.extend([base_URL + ele['href'].encode('utf8')])
            # add the row to the bottom of the dataframe
            df_NYT_abstract.loc[len(df_NYT_abstract)] = one_row
    # save the data frame
    with open('../data/df_NYT_abstract.pickle', 'w') as f:
        cPickle.dump(df_NYT_abstract, f)
    return None

def NYT_cooking_easy_recipe():
    '''
    Scrape the recipe pages using the URLs saved in abstract data frame
    '''
    # unpickle the saved data frame
    with open('../data/df_NYT_abstract.pickle', 'r') as f:
        df_NYT_abstract_unpickled = cPickle.load(f)
    all_soup_100 = []
    for i in xrange(df_NYT_abstract_unpickled.shape[0]):
        SLEEP_TIME = random.uniform(2,4)
        time.sleep(SLEEP_TIME)
        response = requests.get(df_NYT_abstract_unpickled.URL[i])
        # Raise a warning and exit when there is an error
        if response.status_code != 200:
            print 'WARNING', response.status_code
            #print 'Current recipe number is: ', i
            break
        soup = BeautifulSoup(response.content, 'html.parser')
        # append every 100 recipes and create pickle files
        all_soup_100.append(soup)
        j100 = (i + 1) % 100
        # if (i + 1) % 10 == 0:
        #     print "10 pages scrapped!"
        if j100 == 0:
            loop = int((i + 1) / 100)
            # print "this is Loop:", loop
            with open('recipe_100_' + str(loop) + '.pickle', 'w') as f:
                cPickle.dump(all_soup_100, f)
            all_soup_100 = []
            #all_soup.extend(all_soup_100)
    # if it is a normal exit from the for loop above and there are recipes not pickled
    # pickle the remaining recipes
    if ((response.status_code == 200) & (j100 != 0)):
        with open('recipe_100_' + str(loop + 1) + '.pickle', 'w') as f:
            cPickle.dump(all_soup_100, f)
    return None

def get_ingredients(one_recipe):
    '''
    Read one recipe file and extract ingredients
    Return a list of strings of ingredients
    '''
    printable = set(string.printable)
    ing = one_recipe.findAll('li',itemprop="recipeIngredient")
    num_ing = len(ing)
    ingredients = []
    for i in xrange(num_ing):
        ingredient = ing[i].findAll('span')[-1].contents
        if ingredient:  # if the list is not empty
            # remove the parenthesis and the contents in them
            no_paren = re.sub(r'\([^)]*\)', '', ingredient[0].encode('utf8')
            # remove all non-ascii characters
            ingredients.append(filter(lambda x: x in printable, no_paren)).strip().lower())
    return ingredients

def get_procedure(one_recipe):
    '''
    Read one recipe file and extract cooking procedure
    Return a string of all steps
    '''
    printable = set(string.printable)
    ste = one_recipe.findAll('ol',itemprop="recipeInstructions",class_='recipe-steps')
    step_len = len(ste[0].contents)
    steps = ''
    for i in xrange(1, (step_len + 1) / 2):
        # add a space between the sentences for easy split
        steps += ste[0].contents[2*i-1].contents[0].encode('utf8') + ' '
    # remove non-ascii characters
    return filter(lambda x: x in printable, steps)

def cleanup_ingredients(df):
    '''
    Input: uncleaned df_NYT_easy_complete
    Output: df_NYT_easy_complete with cleaned ingredients list
    # There are some ingredients that are not extracted succeefully
    # The extracted part is a long sentence
    # Need to extract the ingredients from the sentences
    # First create a list of all ingredients, then check if there are ingredients
    # in the long sentences. If any, add those ingredients.
    # Then remove the long sentences
    '''
    # get the list of all the ingredients
    ing = set([item for sublist in list(df['Ingredients']) for item in sublist])
    # get all the ingredients with short names (long names need further extraction)
    short_ing = [i for i in ing if len(i.split()) <= 2]
    # check all ingredients in all recipes for long unextracted sentences
    num_row = df.shape[0]
    for i in xrange(num_row):
        for ing in df['Ingredients'][i]:
            # check all long sentences in 'ingredients'
            if len(ing.split()) > 2:
                # go through the complet ingredient list
                for s in short_ing:
                    # for this recipe, if there are new ingredients in the long sentences, add them
                    if (s in ing) and (s not in df['Ingredients'][i]):
                        df['Ingredients'][i].append(s)
                # delete the long sentences anyway
                df['Ingredients'][i].remove(ing)
    return df

def my_tokenizer(serie):
    '''
    Input: one row of the data frame with cleaned ingredients
    Output: list of strings of verbs, which are:
            1. in lowercase
            2. stemmized (PorterStemmer)
            3. with at least 3 characters
            4. non-unicode
            and strings of nouns (ingredients), which are:
            1. split into single word
            2. stemmized
            3. unique
            4. non-unicode
    '''
    sw = stopwords.words('english')
    PS = PorterStemmer()
    # remove parenthesis, then get the tagged words
    tagged = TextBlob(re.sub(r'\([^)]*\)', '', serie.steps)).tags
    # get the tokens
    verbs = [PS.stem(i[0].lower()).encode('utf8') for i in tagged \
        if (len(i[0]) > 2) and ('V' in i[1]) and (i[0] not in sw)]
    nouns = list(set([PS.stem(item).encode('utf8') \
        for sublist in serie.Ingredients for item in sublist.split()]))
    # the list of missing key words, found by manual inspection
    extra = ['heat', 'cool']
    return verbs + nouns + extra

def NYT_easy_abstract_df_complete():
    '''
    Read the abstract pickle, add ingredients and steps as new columns,
    do some cleaning on the data, and create new features
    '''
    with open('../data/df_NYT_abstract.pickle', 'r') as f:
        df_NYT_abstract_unpickled = cPickle.load(f)
    # create a new list for the extracted info of ingredients and steps
    new_data = []
    for i in xrange(1, 37):
        with open('recipe_100_' + str(i) + '.pickle', 'r') as f:
            df_NYT_recipe_unpickled = cPickle.load(f)
        for j in xrange(len(df_NYT_recipe_unpickled)):
            ingredients = get_ingredients(df_NYT_recipe_unpickled[j])
            steps = get_procedure(df_NYT_recipe_unpickled[j])
            new_data.append([ingredients, steps])
    # add new columns "Ingredients" and "steps" to the abstract data frame
    df_new_data = pd.DataFrame(new_data)
    df_new_data.columns = ['Ingredients','steps']
    df_NYT_easy_complete_uncleaned = df_NYT_abstract_unpickled.join(df_new_data)
    # clean up the ingredients
    df_NYT_easy_complete_cleaned = cleanup_ingredients(df_NYT_easy_complete_uncleaned)
    # add a new column "tokens"
    df_NYT_easy_complete = df_NYT_easy_complete_cleaned.copy()
    df_NYT_easy_complete['Tokens'] = df_NYT_easy_complete.apply(lambda x: my_tokenizer(x))
    # save the finl product
    with open('../data/df_NYT_easy_with_tokens_wb.pickle', 'wb') as f:
        cPickle.dump(df_NYT_easy_complete, f)



if __name__ == '__main__':
    # check if the search pages have already been scrapped, if not, scrape the pages
    if not os.path.isfile('../data/easy_titles.pickle'):
        NYT_easy_abstract()

    # check if the abstract data frame has already been created, if not, create it
    if not os.path.isfile('../data/df_NYT_abstract.pickle'):
        NYT_easy_abstract_df()

    # check if the recipes have been scrapped, if not, scrap them
    if not os.path.isfile('../data/recipe_100_1.pickle'):
        NYT_cooking_easy_recipe()

    # check if the complete data frame have been created, if not, create it
    if not os.path.isfile('../data/df_NYT_easy_complete.pickle'):
        NYT_easy_abstract_df_complete()
