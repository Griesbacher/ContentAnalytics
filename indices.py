INDEX_ALL_FILTERED_STEMED = "index_all_filtered_stemed"
INDEX_ALL_FILTERED_LEMED = "index_all_filtered_lemed"
INDEX_ALL_FILTERED = "index_all_filtered"
INDEX_ALL_FILTERED_CERTAIN = "index_all_filtered_certain"
INDEX_ALL_FILTERED_CERTAIN_LEMED = "index_all_filtered_certain_lemed"
INDEX_ALL_FILTERED_SPELLED_LEMED = "index_all_filtered_spelled_lemed"
INDEX_ALL_FILTERED_CERTAIN_SPELLED_LEMED = "index_all_filtered_certain_spelled_lemed"
INDEX_60k_FILTERED_STEMED = "index_60k_filtered_stemed"
INDEX_60k_FILTERED_LEMED = "index_60k_filtered_lemed"
INDEX_60k_FILTERED = "index_60k_filtered"
INDEX_60k_FILTERED_CERTAIN = "index_60k_filtered_certain"
INDEX_60k_FILTERED_CERTAIN_LEMED = "index_60k_filtered_certain_lemed"
INDEX_60k_FILTERED_SPELLED_LEMED = "index_60k_filtered_spelled_lemed"
INDEX_60k_FILTERED_CERTAIN_SPELLED_LEMED = "index_60k_filtered_certain_spelled_lemed"


def get_all_indices():
    # type: () -> list
    result = list()
    for k, v in globals().iteritems():
        if k.startswith("INDEX"):
            result.append(v)
    result.sort(lambda y, x: cmp(len(x), len(y)))
    return result


def get_60k_indices():
    # type: () -> list
    result = list()
    for i in get_all_indices():
        if "_60k_" in i:
            result.append(i)
    return result
