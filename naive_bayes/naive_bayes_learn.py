from __future__ import division

import json
import re
from timeit import default_timer as timer

from document_termvector_iterators import elasticsearch_dti


def learn_naive_bayes(model_file_path, document_termvector_iterator, dti_pargs=(), dti_nargs=None):
    """
    Creates a model for classification using naive bayes algorithm.

    :param model_file_path: path to the file to write model data to
    :param document_termvector_iterator: an iterator that iterates over 
            tuples of training documents and their term vectors
    :param dti_pargs: positional arguments for the iterator
    :param dti_nargs: named arguments for the iterator
    """
    vocabulary = set()
    classes_regex = "^(w[1-4])|(k[0-9]|(1[0-5]))|(s[1-5])$"
    class_termvectors = {}
    docs_per_class = {}
    all_docs = 0
    current = 0
    time = timer()
    smoothpersecond = None
    docs_and_termvectors = document_termvector_iterator(*dti_pargs, **dti_nargs if dti_nargs else {})

    for document, doc_termvector, doc_count in docs_and_termvectors:
        # determine which classes this document has (treat classes as binary)
        document_classes = {class_name: float(is_class) >= 0.5
                            for class_name, is_class in document.iteritems()
                            if re.match(classes_regex, class_name)}

        # add new terms to the vocabulary
        vocabulary.update(doc_termvector.keys())

        # aggregate termvectors for each class
        for class_name, is_class in document_classes.iteritems():
            this_class_termvector = class_termvectors.get(class_name, {"positive_terms": {}, "negative_terms": {}})
            for term, count in doc_termvector.iteritems():
                category = "positive_terms" if is_class else "negative_terms"
                this_class_termvector[category][term] = this_class_termvector[category].get(term, 0) + count
            class_termvectors[class_name] = this_class_termvector
            if is_class:
                docs_per_class[class_name] = docs_per_class.get(class_name, 0) + 1
        all_docs += 1

        current += 1
        if current % 100 == 0:
            persecond = int(100 // (timer() - time))
            smoothpersecond = persecond if smoothpersecond is None else int(smoothpersecond * 0.85 + persecond * 0.15)
            resttime = int((doc_count - current) // smoothpersecond)
            restminutes = resttime // 60
            restseconds = resttime - (restminutes * 60)
            print "processed {current}/{doc_count} documents, {smoothpersecond}/s, " \
                  "{restminutes}:{restseconds:02} mins left".format(**locals())
            time = timer()

    print "learned a vocabulary of {0} unique terms".format(len(vocabulary))
    print "calculating probabilities for learned term vectors"
    for cls, term_vec in class_termvectors.iteritems():
        # add class probabilities
        docs_in_class = docs_per_class[cls] if cls in docs_per_class else 0
        term_vec.update({"class_probability": docs_in_class / all_docs})
        # calculate probabilities for the term vectors
        keys = ("positive_terms", "negative_terms")
        for key in keys:
            N = sum(term_vec[key].values())
            M = len(vocabulary)
            for term in term_vec[key]:
                term_vec[key][term] = (term_vec[key][term] + 1) / (N + M)

    # write the model to a json file
    print "writing the model file"
    with open(model_file_path, "w") as model_file:
        model = {
            "vocabulary_size": len(vocabulary),
            "classes": class_termvectors
        }
        json.dump(model, model_file, indent=4)


if __name__ == '__main__':
    learn_naive_bayes("model.json", elasticsearch_dti, ("tweets", "tweet"), {"max_docs": None})
