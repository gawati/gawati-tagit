#!/usr/bin/env python3
# Tool to:
# a. Bulk convert xml contents to clean text
# b. Train a tf-idf (term frequency - inverse document frequency) model with the given corpus
# c. Generate tags for a given document. Updates dictionary with the new doc.


import argparse
import glob
import os
import subprocess
from shutil import rmtree
from sys import argv
from gensim import models, corpora
from collections import defaultdict
from stop_words import safe_get_stop_words

data_text_dir = 'data/akn_text'
stopwords_dir = 'stopwords'
lang_map = {
  'eng': 'en',
  'fra': 'fr'
}


def get_dict_name(lang):
  return "tagit.dict" + "." + lang

def get_model_name(lang):
  return "tagit.model" + "." + lang

def stopwords_extended(lang):
  esw_file = os.path.join(stopwords_dir, lang)
  if os.path.exists(esw_file):
    with open(esw_file, 'r') as f:
      sw = f.read()
      return sw.split("\n")
  return []

def prune_stopwords(doc, lang='en'):
  if lang in lang_map:
    lang = lang_map[lang]
  stoplist = safe_get_stop_words(lang) + stopwords_extended(lang)
  return [word for word in doc.lower().split() if word not in stoplist]

def prepare_corpus(data_dir, lang):
  raw_corpus = []
  for file in glob.glob(data_dir+'/**/*', recursive=True):
    with open(file, 'r') as f:
      doc = prune_stopwords(f.read(), lang)
      raw_corpus.append(doc)
  
  # Count word frequencies across all documents
  frequency = defaultdict(int)
  for doc in raw_corpus:
    for token in doc:
      frequency[token] += 1

  # Only keep words that appear more than once
  processed_corpus = [[token for token in doc if frequency[token] > 1] for doc in raw_corpus]
  return processed_corpus

def train(data_dir, lang):
  processed_corpus = prepare_corpus(data_dir, lang)

  # Prepare Vocabulary
  dictionary = corpora.Dictionary(processed_corpus)
  dictionary.save(get_dict_name(lang))
  # Print tokens with ID
  # print("\n Vocabulary: \n", dictionary.token2id)

  # Create Vectors.
  bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
  # print("\n Document Vectors: \n", bow_corpus)

  # Train Model  
  tfidf = models.TfidfModel(bow_corpus)
  tfidf.save(get_model_name(lang))

def tag_doc(ip_file):
  op_tmp = 'op_tmp'
  lang = getFileMeta(ip_file)["lang"]

  if ip_file.split(".")[-1:] == ['txt']:
    op_tmp = ip_file
  else:
    # Convert xml to clean text
    with open(op_tmp, 'w') as f:
        subprocess.check_call(['perl', 'xml2txt.pl', ip_file], stdout=f)

  with open(op_tmp, 'r') as f:
    new_doc = f.read()

  new_doc_processed = prune_stopwords(new_doc, lang)

  try: 
    tagit_model = models.TfidfModel.load(get_model_name(lang))
    tagit_dict = corpora.Dictionary.load(get_dict_name(lang))
  except FileNotFoundError:
    return {'error': 'Language not supported'}

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
  return {'tags': tags[:10]}

def xml2txt(ip_dir):
  # Remove old files
  for file in glob.glob(data_text_dir+'/*'):
    rmtree(file)

  # Extract clean text from xml
  for i, ip_file in enumerate(glob.glob(ip_dir+'/**/*', recursive=True)):
    if not os.path.isdir(ip_file):
      print(ip_file)
      op_meta = getFileMeta(ip_file)
      op_file = os.path.join(data_text_dir, op_meta["lang"], op_meta["filename"] + ".txt")
      ensure_path(op_file)
      with open(op_file, 'w') as f:
        subprocess.check_call(['perl', 'xml2txt.pl', ip_file], stdout=f)

def ensure_path(fpath):
  if not os.path.exists(os.path.dirname(fpath)):
    try:
        os.makedirs(os.path.dirname(fpath))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

def getFileMeta(fname):
  op_fname = fname.replace("/", "_").replace("@", "")
  op_fname = os.path.splitext(op_fname)[0]
  try:
    lang = op_fname.split("_")[-2]
  except IndexError:
    lang = 'en'
  return {"filename": op_fname, "lang": lang}

def is_valid_dir(parser, arg):
  if not os.path.exists(arg):
    parser.error("The dir %s does not exist!" % arg)
  else:
    return arg

def main():
  parser = argparse.ArgumentParser(description='Tool to train tf-idf model')
  parser.add_argument('--convert', dest="xml_dir",
                      help="Input XML data folder to convert to text", metavar="data_folder", type=lambda x: is_valid_dir(parser, x))
  parser.add_argument('--train', help="Train model for input data folder",
                      dest="train", nargs=2, metavar=('data_folder','lang'))
  parser.add_argument('--tag', dest="doc",
                      help="Input document to tag", metavar="doc",
                      type=lambda x: is_valid_dir(parser, x))
  args = parser.parse_args()

  if len(argv) < 2:
    parser.print_help()

  if args.xml_dir:
    print("Converting xml to clean text")
    xml2txt(args.xml_dir)

  if args.train:
    data_dir = args.train[0]
    lang = args.train[1]
    if is_valid_dir(parser, data_dir):
      print("Training tf-idf model with corpus {0}, in language {1}".format(data_dir, lang))
      train(data_dir, lang)

  if args.doc:
    print("Inferring tags for document {0}".format(args.doc))
    print(tag_doc(args.doc))

if __name__== "__main__":
  main()