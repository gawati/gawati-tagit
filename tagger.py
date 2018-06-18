#!/usr/bin/env python3
# Generates tags for a document using tf-idf (term frequency - inverse document frequency) model
# Ignores words not present in the trained vocab dictionary.

# DATA / DOCUMENTS
raw_corpus = ["Human machine interface for lab abc computer applications",
             "A survey of user opinion of computer system response time",
             "The EPS user interface management system",
             "System and human system engineering testing of EPS",              
             "Relation of user perceived response time to error measurement",
             "The generation of random binary unordered trees",
             "The intersection graph of paths in trees",
             "Graph minors IV Widths of trees and well quasi ordering",
             "Graph minors A survey"]


# PREPARE CORPUS
# Create a set of frequent words
stoplist = set('for a of the and to in'.split(' '))
# Lowercase each document, split it by white space and filter out stopwords
texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in raw_corpus]

# Count word frequencies
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

# Only keep words that appear more than once
processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]
processed_corpus

from gensim import corpora
dictionary = corpora.Dictionary(processed_corpus)

# Print tokens with ID
print("\n Vocabulary: \n", dictionary.token2id)

# CREATE VECTORS
# Convert corpus to list of vectors
bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
print("\n Document Vectors: \n", bow_corpus)


# TRAIN MODEL
from gensim import models
# train the model
tfidf = models.TfidfModel(bow_corpus)

# TEST NEW DOC
new_doc = "the testing of system trees"
print("\n Applying the tfidf model on a new doc string: \n `{0}`".format(new_doc))
# remove stopwords
new_doc_processed = [word for word in new_doc.lower().split() if word not in stoplist]
# transform the `new_doc` by applying the above model
new_doc_transformed = tfidf[dictionary.doc2bow(new_doc_processed)]
print("\n Weighted vectors for the new doc: \n", new_doc_transformed)

# Sort in descending order of weights
from operator import itemgetter
new_doc_sorted = sorted(new_doc_transformed, key=itemgetter(1), reverse=True)

# Print the tokens of `new_doc` in descending order of weights  
id_tokens = dictionary.token2id
print("\n Tags for new doc in descending order of weights:")
for i,j in new_doc_sorted:
  print(" ", list(id_tokens.keys())[list(id_tokens.values()).index(i)])
