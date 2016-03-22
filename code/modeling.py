import cPickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.grid_search import GridSearchCV

def preprocessing():
    '''
    Create features from tfidf
    '''
    with open('../data/df_NYT_easy_with_tokens_wb.pickle', 'rb') as f:
        df = cPickle.load(f)
    # vocabulary list for dfidf
    vocab = list(set([item for sublist in df['Tokens'].values for item in sublist]))
    # tfidf using vocabulary
    tfidf_vectorizer = TfidfVectorizer(vocabulary=vocab)
    tfidf = tfidf_vectorizer.fit_transform(df['steps'])
    # create new data frame of features
    df_features = pd.DataFrame(tfidf.todense())
    df_features.columns = vocab
    df_with_features = df.join(df_features)
    with open('../data/df_with_features.pkl', 'wb') as f:
        cPickle.dump(df_with_features, f)

def model_select():
    # print out cross validation scores of different models
    # and return the fit best model (random forest model)
    with open('../data/df_with_features.pkl', 'rb') as f:
        df = cPickle.load(f)
    # get the rows that can be used for training
    # the cooking should not be more than 2 hours
    df_with_time = df[(df['Time']>0) & (df['Time'] <= 120)]
    X = np.array(df_with_time.iloc[:, 8:])
    y = df_with_time['Time'].values
    model_linear = LinearRegression(fit_intercept=True, normalize=True, copy_X=True, n_jobs=1)
    print cross_val_score(model_linear, X, y, scoring='r2', cv=10)
    model_abr = AdaBoostRegressor(base_estimator=None, n_estimators=50, learning_rate=1.0, loss='linear', random_state=None)
    print cross_val_score(model_abr, X, y, scoring='r2', cv=10)
    model_gbr = GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=100, \
                        subsample=1.0, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, \
                        max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, \
                        max_leaf_nodes=None, warm_start=False, presort='auto')
    print cross_val_score(model_gbr, X, y, scoring='r2', cv=10)
    model_rfr = RandomForestRegressor(n_estimators=10, criterion='mse', max_depth=None, min_samples_split=2, \
                min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, \
                bootstrap=True, oob_score=False, n_jobs=1, random_state=None, verbose=0, warm_start=False)
    print cross_val_score(model_rfr, X, y, scoring='r2',cv=10)
    model_rfr.fit(X, y)
    return df, model_rfr

def time_estimate(df, best_model):
    '''
    Create a new data frame with estimated time
    '''
    X_all = np.array(df.iloc[:, 8:])
    y_pred = model_rfr.predict(X_all)
    # keep only the original columns when adding new column
    df_pred = pd.concat([df.iloc[:,:8], pd.Series(y_pred)],axis=1)
    # add column name
    column_names = df_pred.columns.values
    column_names[-1] = 'estimated_time'
    df_pred.columns = column_names

    # I decided to add pictures to my web_app after the model was trained.
    # Add the links to the images as the very last step
    # to minimize the modification to the code and data
    with open('../data/easy_titles.pickle', 'r') as f:
        all_soup_unpickled = cPickle.load(f)
    img_link = [i.contents[0]['data-large'].encode('utf8') \
             for j in all_soup_unpickled for i in j.findAll(class_="image")]
    # there are invalid links, which do not start with "http"
    img_link_clean = [re.sub(r'^(?!http).*', '', i) for i in img_link]
    df_pred = pd.concat([df_pred, pd.Series(img_link_clean)],axis=1)
    column_names = df_pred.columns.values
    column_names[-1] = 'img_link'
    df_pred.columns = column_names
    with open('../data/df_final.pkl', 'wb') as f:
        cPickle.dump(df_pred, f)

def model_grid_search():
    # Ada Boosting
    abr_grid = {'learning_rate': [0.01, 0.1, 1, 5],
            'n_estimators': [50, 100, 500, 1000, 2000],
            'loss': ['linear', 'square', 'exponential']}
    abr_gridsearch = GridSearchCV(AdaBoostRegressor(),
                                 abr_grid,
                                 n_jobs=-1,
                                 verbose=True,
                                 scoring='mean_squared_error')
    abr_gridsearch.fit(X, y)
    print("best parameters:", abr_gridsearch.best_params_)
    # ('best parameters:', {'n_estimators': 50, 'loss': 'exponential', 'learning_rate': 0.01})
    best_abr_model = abr_gridsearch.best_estimator_

    # Gradient Boosting
    gbr_grid = { 'loss': ['ls','lad','huber'],
            'learning_rate': [0.01, 0.1, 1, 5],
            'n_estimators': [50, 100, 500, 1000, 2000],
            'max_features': ['auto', 'sqrt', 'log2']}
    gbr_gridsearch = GridSearchCV(GradientBoostingRegressor(),
                                 gbr_grid,
                                 n_jobs=-1,
                                 verbose=True,)
    gbr_gridsearch.fit(X, y)
    print("best parameters:", gbr_gridsearch.best_params_)
    # ('best parameters:', {'max_features': 'sqrt', 'n_estimators': 1000, 'learning_rate': 0.01})
    best_gbr_model = gbr_gridsearch.best_estimator_

    # Random Forest
    rfr_grid = { 'max_depth': [1,2,3],
            'n_estimators': [50, 100, 500, 1000, 2000],
            'max_features': ['auto', 'sqrt', 'log2']}
    rfr_gridsearch = GridSearchCV(RandomForestRegressor(),
                                 rfr_grid,
                                 n_jobs=-1,
                                 verbose=True)
    rfr_gridsearch.fit(X, y)
    print("best parameters:", rfr_gridsearch.best_params_)
    # ('best parameters:', {'max_features': 'auto', 'n_estimators': 50, 'max_depth': 3})
    best_rfr_model = rfr_gridsearch.best_estimator_
    return None

if __name__ == '__main__':
    # check if the data frame with tfidf has already been created, if not, create it
    if not os.path.isfile('../data/df_with_features.pkl'):
        preprocessing()
    # split the data set
    df, model = model_select()
    time_estimate(df, model)
