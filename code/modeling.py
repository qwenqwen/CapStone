import cPickle
from sklearn.cross_validation import train_test_split

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

def dataset_split():
    with open('../data/df_with_features.pkl', 'rb') as f:
        df = cPickle.load(f)
    # get the rows that can be used for training
    df_with_time = df[df['Time']>0]
    X_train, X_test, y_train, y_test = train_test_split(np.array(df_with_time.iloc[:, 8:]), \
        df_with_time['Time'].values, test_size=0.2, random_state=100)
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    # check if the data frame with tfidf has already been created, if not, create it
    if not os.path.isfile('../data/df_with_features.pkl'):
        preprocessing()
    # split the data set
    X_train, X_test, y_train, y_test = dataset_split()
