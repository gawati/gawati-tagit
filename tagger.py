#!/usr/bin/env python3
# Tool to:
# a. Bulk convert xml contents to clean text
# b. Train a tf-idf (term frequency - inverse document frequency) model with the given corpus
# c. Generate tags for a given document
# Ignores words not present in the trained vocab dictionary.
# To-Do: 
# a. Update vocab for a new doc
# b. Bigger list of stopwords


import argparse
import glob
import os
import subprocess
from sys import argv
from gensim import models, corpora
from collections import defaultdict

data_text_dir = 'data/akn_text'
stoplist = set('for a of the and to in'.split(' '))

def prune_stopwords(doc):
  return [word for word in doc.lower().split() if word not in stoplist]

def prepare_corpus():
  raw_corpus = []
  for file in glob.glob(data_text_dir+'/**/*', recursive=True):
    with open(file, 'r') as f:
      raw_corpus.append(f.read())
  
  texts = [prune_stopwords(document) for document in raw_corpus]
  
  # Count word frequencies across all documents
  frequency = defaultdict(int)
  for text in texts:
    for token in text:
      frequency[token] += 1

  # Only keep words that appear more than once
  processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]
  return processed_corpus

def train():
  processed_corpus = prepare_corpus()

  # Prepare Vocabulary
  dictionary = corpora.Dictionary(processed_corpus)
  dictionary.save('tagit.dict')
  # Print tokens with ID
  # print("\n Vocabulary: \n", dictionary.token2id)

  # Create Vectors.
  bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
  # print("\n Document Vectors: \n", bow_corpus)

  # Train Model  
  tfidf = models.TfidfModel(bow_corpus)
  tfidf.save("tagit.model")

def tag_doc(ip_file):
  op_tmp = 'op_tmp'
  # Convert xml to clean text
  with open(op_tmp, 'w') as f:
      subprocess.check_call(['perl', 'xml2txt.pl', ip_file], stdout=f)

  with open(op_tmp, 'r') as f:
    new_doc = f.read()

  new_doc_processed = prune_stopwords(new_doc)
  tagit_model = models.TfidfModel.load("tagit.model")
  tagit_dict = corpora.Dictionary.load("tagit.dict")

  # transform the `new_doc` by applying the above model
  new_doc_transformed = tagit_model[tagit_dict.doc2bow(new_doc_processed, allow_update=True)]
  # print("\n Weighted vectors for the new doc: \n", new_doc_transformed)

  # Sort in descending order of weights
  from operator import itemgetter
  new_doc_sorted = sorted(new_doc_transformed, key=itemgetter(1), reverse=True)

  # Tokens of `new_doc` in descending order of weights  
  id_tokens = tagit_dict.token2id
  tags = []
  for i,j in new_doc_sorted:
    word = list(id_tokens.keys())[list(id_tokens.values()).index(i)]
    tags.append(word)
  return tags[:10]

def xml2txt(ip_dir):
  # Remove old files
  for file in glob.glob(data_text_dir+'/*'):
    os.remove(file)
  # Extract clean text from xml
  for i, ip_file in enumerate(glob.glob(ip_dir+'/**/*', recursive=True)):
    print(ip_file)
    op_file = data_text_dir + '/fil' + str(i)
    with open(op_file, 'w') as f:
      subprocess.check_call(['perl', 'xml2txt.pl', ip_file], stdout=f)

def is_valid_dir(parser, arg):
  if not os.path.exists(arg):
    parser.error("The dir %s does not exist!" % arg)
  else:
    return arg

def main():
  parser = argparse.ArgumentParser(description='Tool to train tf-idf model')
  parser.add_argument('--convert', dest="xml_dir",
                      help="Input XML data folder to convert to text", metavar="CONVERT", type=lambda x: is_valid_dir(parser, x))
  parser.add_argument('--train', help="Train model",
                      dest="train", action='store_true')
  parser.add_argument('--tag', dest="doc",
                      help="Input document to tag", metavar="TAG",
                      type=lambda x: is_valid_dir(parser, x))
  args = parser.parse_args()

  if len(argv) < 2:
    parser.print_help()

  if args.xml_dir:
    print("Converting xml to clean text")
    xml2txt(args.xml_dir)

  if args.train:
    print("Training tf-idf model with corpus {0}".format(data_text_dir))
    train()

  if args.doc:
    print("Inferring tags for document {0}".format(args.doc))
    print(tag_doc(args.doc))

if __name__== "__main__":
  main()