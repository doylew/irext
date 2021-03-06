# Functions which deal with classification and evaluation
from IPython.display import display
from sklearn.svm import SVC
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.datasets import fetch_20newsgroups
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.svm import LinearSVC

def calculate_category_probability(train_df, cat_map, number_of_cats = 25):
    # map ['category'] => probability
    cat_probs = dict()
    # estimate the number of categories initialize the dict
    for i in range(0,1000000):
        # initialize them to be at count zero
        cat_probs[i] = 1.0
    # go through the training set keep track of counts
    for category in train_df.ix[:,1]:
        cat_probs[category] = cat_probs[category] + 1
    # now we take a naive approach and divide by number of
    # categories to get a probability of pulling the specific category
    for i in range(0,1000000):
        # if it isn't the intialized value then we have a valid
        # probability to use during the training of the vectors
        if cat_probs[i] != 1.0:
            cat_probs[i] = float(cat_probs[i] / float(number_of_cats))
    return cat_probs


def run_ec(train_df, test_df, cat_map):
    # various parameters to be searched over for optimization
    parameters = {'vect__ngram_range': [(1,1), (1,2)],
                'tfidf__use_idf': (True, False),}

    # ec pipeline for evaluation
    text_clf = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf', OneVsRestClassifier(SVC(kernel='linear'))),])

    probabilities = calculate_category_probability(train_df, cat_map)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(train_df.ix[:,0])
    X_train_counts.shape
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    X_train_tfidf.shape
    # calculate the eigen value decomposition 
    pca = TruncatedSVD(algorithm='arpack', n_components=1, n_iter=7, random_state=42)
    pca.fit(X_train_tfidf)
    vari = pca.explained_variance_ratio_[0]
    sing = pca.singular_values_[0]
    text_clf = text_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    predicted = text_clf.predict(test_df.ix[:,0])
    # evaluate_accuracy(test_df, predicted, cat_map, format_string = "EC")
    print("Searching over parameters for optimization...")
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    gs_clf = gs_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    # print("Naive Bayes Score: " + str(gs_clf.best_score_))
    # print("Params Chosen: " + str(gs_clf.best_params_))
    scores = cross_val_score(gs_clf, test_df.ix[:,0], test_df.ix[:,1], cv=10)
    print("EC Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))



def run_naive_bayes(train_df, test_df, cat_map, traindata, testdata):
    # various parameters to be searched over for optimization
    parameters = {'vect__ngram_range': [(1,1), (1,2)],
                'tfidf__use_idf': (True, False),
                'clf__alpha': (1e0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5),}

    # Naive Bayes pipeline for evaluation
    text_clf = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf', MultinomialNB()),])

    text_clf = text_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    predicted = text_clf.predict(test_df.ix[:,0])
    
    # evaluate_accuracy(test_df, predicted, cat_map, format_string = "Naive Bayes")
    print("Searching over parameters for optimization...")
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    gs_clf = gs_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    
    # print("Naive Bayes Score: " + str(gs_clf.best_score_))
    # print("Params Chosen: " + str(gs_clf.best_params_))
    scores = cross_val_score(gs_clf, test_df.ix[:,0], test_df.ix[:,1], cv=10)
    print("Naive Bayes Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def run_multi_naive_bayes(train_df, test_df, cat_map, traindata, testdata):
    # various parameters to be searched over for optimization
    parameters = {'vect__ngram_range': [(1,1), (1,2)],
            'tfidf__use_idf': (True, False)}

    # multi-class Naive Bayes pipeline
    text_clf = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf', OneVsRestClassifier(MultinomialNB())),])

    text_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    predicted = text_clf.predict(test_df.ix[:,0])
    # evaluate_accuracy(test_df, predicted, cat_map, format_string = "Multi-Naive Bayes")

    # print("Searching over parameters for optimization...")
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    gs_clf = gs_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    # print("Multi-Naive Bayes Score: " + str(gs_clf.best_score_))
    # print("Params Chosen: " + str(gs_clf.best_params_))
    scores = cross_val_score(gs_clf, test_df.ix[:,0], test_df.ix[:,1], cv=10)
    print("Multi Naive Bayes Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def run_multi_svm(train_df, test_df, cat_map, traindata, testdata):
    # various parameters to be searched over for optimization
    parameters = {'vect__ngram_range':[(1,1), (1,2)],
                'tfidf__use_idf': (True, False),}

    # multi-class SVM pipeline
    text_clf = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf', OneVsRestClassifier(LinearSVC(loss='hinge', penalty='l2',
                            tol=1e-3, random_state=42, max_iter=1000)))])

    text_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    predicted = text_clf.predict(test_df.ix[:,0])
    # evaluate_accuracy(test_df, predicted, cat_map, format_string = "Multi-SVM")

    # print("Searching over parameters for optimization...")
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    gs_clf = gs_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    # print("Multi-SVM Score: " + str(gs_clf.best_score_))
    # print("Params Chosen: " + str(gs_clf.best_params_))
    scores = cross_val_score(gs_clf, test_df.ix[:,0], test_df.ix[:,1], cv=10)
    print("Mutli SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def run_svm(train_df, test_df, cat_map, traindata, testdata):
    #various parameters to be searched over for optimization
    parameters = {'vect__ngram_range':[(1,1), (1,2)],
                'tfidf__use_idf': (True, False),
                'clf-svm__alpha':(1e0, 1e-1, 1e-2, 1e-4, 1e-5),}

    # SVM (gradient descent) pipeline for evaluation
    text_clf_svm = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',
                            alpha=1e-3, max_iter=1000, tol=1e-3, random_state=42)),])

    text_clf_svm.fit(train_df.ix[:,0], train_df.ix[:,1])
    predicted = text_clf_svm.predict(test_df.ix[:,0])
    # evaluate_accuracy(test_df, predicted, cat_map, format_string = "SVM")

    # print("Searching over parameters for optimization...")
    gs_clf = GridSearchCV(text_clf_svm, parameters, n_jobs=-1)
    gs_clf = gs_clf.fit(train_df.ix[:,0], train_df.ix[:,1])
    # print("SVM Score: " + str(gs_clf.best_score_))
    # print("Params Chosen: " + str(gs_clf.best_params_))
    scores = cross_val_score(gs_clf, test_df.ix[:,0], test_df.ix[:,1], cv=10)
    print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def evaluate_accuracy(test_df, predicted, cat_map, format_string =""):
    # calculate simple accuracy of the given predictions
    correct = 0.0
    number = 0.0
    # for each of the 
    for doc,category in zip(test_df.ix[:,1], predicted):
        if cat_map[doc] == cat_map[category]:
            correct = correct + 1.0
        number = number + 1.0
    print(format_string, " Accuracy:", float(correct/number))

def learn_top_k_categories(train, test, cat_map, k = 25):
    # keep a dictionary of counts for the category
    # 10,000 is an estimate of how many categories 
    category_counts = dict()
    for i in range(0,1000000):
        # initialize them all to begin at count zero
        category_counts[i] = 0
    # iterate over the training set and count the categories
    for (page_name, categories) in train.items():
        for category in categories:
            category_counts[category] = category_counts[category] + 1
    # iterate over the test set and count the categories
    for (page_name, categories) in test.items():
        for category in categories: 
            category_counts[category] = category_counts[category] + 1
    # create a set for the top k categories
    top_k = set()
    # go through the category counts and find those which have
    # more than 20 data points, estimate can be changed
    for (category, count) in category_counts.items():
        if count > 20:
            if len(top_k) >= k:
                top_k_copy = top_k.copy()
                for cat in top_k_copy:
                    if category_counts[cat] < count:
                        top_k.remove(cat)
                        top_k.add(category)
            else:
                top_k.add(category)
    print("Top " + str(len(top_k)) + " categories retrieved!")
    return top_k


