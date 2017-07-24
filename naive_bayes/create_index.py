"""
Reads some sample files and creates an elastic search index
"""
import requests

from document_iterator import iterate, data_count


def create_index(data_path, index_name, index_type, protocol="http", address="localhost", port=9200, verbose=False):
    session = requests.Session()

    # delete existing index
    answer = session.delete("%s://%s:%s/%s" % (protocol, address, port, index_name)).content
    if verbose:
        print answer

    # add all documents to the index, beginning with index 1
    document_id = 1
    document_count = data_count(data_path)
    for item in iterate(data_path):
        session.put("%s://%s:%s/%s/%s/%s" % (protocol, address, port, index_name, index_type, document_id), json=item)
        if verbose and document_id % 100 == 0:
            print "indexed %s/%s, %3s%% |%-20s|" % (
                document_id, document_count, document_id * 100 / document_count,
                "-" * (document_id * 20 / document_count))
        document_id += 1
    if verbose:
        print "indexed %s/%s, finished indexing." % (document_id - 1, document_count)


if __name__ == "__main__":
    create_index("train_part.csv", "tweets", "tweet", verbose=True)
