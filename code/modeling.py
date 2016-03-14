import cPickle
from sklearn.cross_validation import train_test_split
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

def dataset_split(testsize, randomstate):
    with open('../data/df_with_features.pkl', 'rb') as f:
        df = cPickle.load(f)
    # get the rows that can be used for training
    # the cooking should not be more than 2 hours
    df_with_time = df[(df['Time']>0) & (df['Time'] <= 120)]
    X_train, X_test, y_train, y_test = train_test_split(np.array(df_with_time.iloc[:, 8:]), \
        df_with_time['Time'].values, test_size=testsize, random_state=randomstate)
    return X_train, X_test, y_train, y_test

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
    abr_gridsearch.fit(X_train, y_train)
    print("best parameters:", abr_gridsearch.best_params_)
    # ('best parameters:', {'n_estimators': 100, 'loss': 'linear', 'learning_rate': 0.01})
    best_abr_model = abr_gridsearch.best_estimator_
v xxxv 


if __name__ == '__main__':
    # check if the data frame with tfidf has already been created, if not, create it
    if not os.path.isfile('../data/df_with_features.pkl'):
        preprocessing()
    # split the data set
    X_train, X_test, y_train, y_test = dataset_split(0.2, 100)
