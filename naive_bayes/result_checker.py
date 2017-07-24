import csv


def check_result(result_path, reference_path, id_key, evalueation_path):
    result_list = {}
    reference_list = {}
    with open(result_path, "rb") as result_file, open(reference_path, "rb") as reference_file:
        result_list = {result[id_key]: result for result in csv.DictReader(result_file)}
        reference_list = {reference[id_key]: reference for reference in csv.DictReader(reference_file)}

    evaluation = {}
    evaluation_case = {
        (1, 1): "a",
        (1, 0): "b",
        (0, 1): "c",
        (0, 0): "d"
    }
    for row_id, result in result_list.iteritems():
        if row_id in reference_list:
            reference = reference_list[row_id]
            for doc_class in [doc_class for doc_class in result if doc_class != id_key]:
                # evaluation[doc_class] = int(result[doc_class]) == int(float(reference[doc_class]) > 0.5)
                res_val = int(result[doc_class])
                ref_val = int(float(reference[doc_class]) > 0.5)
                evaluation[doc_class] = evaluation.get(doc_class, {"a": 0, "b": 0, "c": 0, "d": 0})
                evaluation[doc_class][evaluation_case[res_val, ref_val]] += 1

    with open(evalueation_path, "wb") as evaluation_file:
        csv_keys = ["class", "a", "b", "c", "d", "accuracy", "precision", "recall"]
        writer = csv.DictWriter(evaluation_file, csv_keys)
        writer.writeheader()
        for doc_class, e in evaluation.iteritems():
            e["class"] = doc_class
            e["accuracy"] = (float(e["a"] + e["d"])) / \
                            (e["a"] + e["b"] + e["c"] + e["d"]) if (e["a"] + e["b"] + e["c"] + e["d"]) != 0 else 0
            e["precision"] = float((e["a"])) / (e["a"] + e["b"]) if (e["a"] + e["b"]) != 0 else 0
            e["recall"] = float((e["a"])) / (e["a"] + e["c"]) if (e["a"] + e["c"]) != 0 else 0
            writer.writerow(e)


if __name__ == '__main__':
    check_result("classification_result.csv", "test_part.csv", "id", "evaluation.csv")
