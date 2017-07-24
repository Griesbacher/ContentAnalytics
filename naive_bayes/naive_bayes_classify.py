"""
classify with naive bayes
"""

from __future__ import division

import csv
import json
from decimal import *

import math

from document_termvector_iterators import csv_elasticsearch_dti
from timeit import default_timer as timer

# set decimal precision
getcontext().prec = 30


class Progress(object):
    def __init__(self):
        self.current = 0
        self.time = timer()
        self.smoothpersecond = None

    def update(self, total):
        self.current += 1
        if self.current % 100 == 0:
            persecond = int(100 // (timer() - self.time))
            self.smoothpersecond = persecond if self.smoothpersecond is None else int(
                self.smoothpersecond * 0.85 + persecond * 0.15)
            # noinspection PyTypeChecker
            # because self.smoothpersecond won't be None
            resttime = int((total - self.current) // self.smoothpersecond)
            restminutes = resttime // 60
            restseconds = resttime - (restminutes * 60)
            print "processed {self.current}/{total} documents, {self.smoothpersecond}/s, " \
                  "{restminutes}:{restseconds:02} mins left".format(**locals())
            self.time = timer()


def classify(model_path, result_path, document_termvector_iterator, dti_pargs=(), dti_nargs=None):
    docs_and_termvectors = document_termvector_iterator(*dti_pargs, **dti_nargs if dti_nargs else {})
    model_data = json.loads(open(model_path).read())
    progress = Progress()
    all_document_classes = []

    for document, doc_termvector, doc_count in docs_and_termvectors:
        this_document_classes = {cls: 0 for cls in model_data["classes"]}
        this_document_classes["id"] = document["id"]
        for doc_class in model_data["classes"]:
            positive_probability = negative_probability = 0
            for term, frequency in doc_termvector.iteritems():
                positive_terms = model_data["classes"][doc_class]["positive_terms"]
                negative_terms = model_data["classes"][doc_class]["negative_terms"]
                if term in positive_terms:
                    for i in xrange(frequency):
                        positive_probability += math.log10(positive_terms[term])
                if term in negative_terms:
                    for i in xrange(frequency):
                        negative_probability += math.log10(negative_terms[term])

            class_probability = model_data["classes"][doc_class]["class_probability"]
            positive_probability = 10 ** (math.log10(class_probability) + positive_probability)
            negative_probability = 10 ** (math.log10(1 - class_probability) + negative_probability)
            this_document_classes[doc_class] = 1 if positive_probability > negative_probability else 0
            #this_document_classes[doc_class] = 0

        all_document_classes.append(this_document_classes)

        # show the progress
        progress.update(doc_count)

    # write the result to a csv file
    print "writing the result file"
    with open(result_path, "wb") as result_file:
        writer = csv.DictWriter(result_file, ["id"] + model_data["classes"].keys())
        writer.writeheader()
        writer.writerows(all_document_classes)


if __name__ == '__main__':
    classify("model.json", "classification_result.csv", csv_elasticsearch_dti, ("test_part.csv", "tweets", "tweet"),
             {"max_docs": None})
