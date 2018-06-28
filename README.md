gawati-tagit is a tool generate tags for a given document.

## Dependencies
- Python3
- Perl

## Install
```
pip install -r requirements
``` 

Start Python3 prompt
```
>>> import nltk
>>> nltk.download('punkt')
>>> exit(0)
```

## Run
```
FLASK_APP=app.py flask run --port=5001
```
or
```
python app.py
```

The flask app can be used to upload a document and generate tags for it. 
File types allowed: `.xml` and `.txt`.

You may also use `tagger.py` to:

1. Bulk convert xml files in a folder to clean text. The output clean text files get written to `data/akn_text`.
2. Train a tf-idf (term frequency - inverse document frequency) model with the given corpus. This generates 
    - a dictionary of words (vocabulary) that gets saved as `tagit.dict`
    - a model that gets saved as `tagit.model`  
Training assumes `data/akn_text` containing clean text files is present. 
3. Generate tags for a given document using the above model. This also updates dictionary with the new doc.

For instructions, run 
```
python tagger.py --help
```

**IMPORTANT**: If `tagit.model` isn't present, ensure you train one using the above script, before using the `/tag` API.  

## Tag Document API

Request URL: http://localhost:5001/api/tag  
Method: POST  
Content-Type: multipart/form-data  
Request body: `file: <The binary data contents of the file>`  
Response: On success, 200 with response json `{ tags: <list of tags>}`.  
          On error, 400 Bad Request with response json `{ error: <error message>}`.  

## Notes:
A comparison of tf-idf, doc2vec and fasttext:

1. With tf-idf, we can get a mapping of weighted vectors to words. We return 10 tags with the highest weights. Where as with doc2vec, we get vectors of a fixed size. Haven't found a way to map vectors to words. 

2. doc2vec seems more suitable for clustering similar documents. tf-idf seems more suitable for generating tags for documents. 

3. fasttext also seems mostly suitable for similarity (nearest neighbour) applications. Moreover, the vectors are meant to be generated for the entire text (and not per document) so that context is understood.

5. fasttext has published pre-trained English word vectors and pre-trained models for 157 languages. Unclear how to use them.

6. Need to verify how Gensim performs for other languages.

## In the gawati-editor context
The service would work as follows as part of the gawati-editor workflow:

1. Create a new AKN document
2. Add attachments
3. For each attachment, click extract text. This converts pdf to fulltext.   
Then, the above `/api/tag` API is called to generate tags for the attachment. These tags get saved in the respective fulltext file.
4. When you refresh tags for the main AKN document:
    - it gathers all the tags from the fulltext files of the attachments.
    - it scans the main AKN metadata for all showAs text.
    - all the showAs texts are prefixed to the list of tags.
5. Note that we never run the main AKN metadata through this service.  
