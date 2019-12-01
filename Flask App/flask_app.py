# -*- coding: utf-8 -*-
"""
Author: Darp Raithatha
"""

# Importing the necessary Libraries
from flask import Flask, request, render_template, current_app
from flask import Blueprint
from flask_pager import Pager
import numpy as np
import pandas as pd
import csv
import re
from functools import reduce
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
spacy_nlp = spacy.load('en_core_web_sm')
import os

# Removing Stop words from the text
def stopwords_removal(list):
    filtered_sentence =[] 
    for word in list:
        lexeme = spacy_nlp.vocab[word]
        if lexeme.is_stop == False:
            filtered_sentence.append(word) 
    return filtered_sentence

# Removes the spaces, Exclamation marks etc.
def preprocess_string(string):
    return re.sub('[^a-zA-Z0-9\s+]+','',string)

# Tokenize the String
def tokenize(query):
    doc = spacy_nlp(query)
    tokens = [token.text for token in doc]
    return tokens

# Indexing the Dataset
def index(file):
    inverted_index ={}
    documents=[]
    with open(file,encoding='utf-8') as f:
            reader = csv.reader(f,delimiter=',')
            next(reader)
            for i, row in enumerate(reader):
                document={}
                document['url']=row[0]
                document['Name']=row[1]
                document['Description']= " ".join(preprocess_string(row[2]).split())
                document['img_url'] = row[3]
                document['img_name']=row[4]
                document['Price'] = row[5]
                
                documents.append(document)
                #print(len(document['Description']))
                
                string = row[1]+ ' ' + row[2]
                string = preprocess_string(string)
                string = [word.lower() for word in string.split()]
                string = " ". join(string)
                text = tokenize(string)
                text = stopwords_removal(text)
                text = list(set(text))
                
                for word in text:
                    if word not in inverted_index:
                        inverted_index[word] = []
                        inverted_index[word].append(i)
                    else:
                        inverted_index[word].append(i)
                        
    return inverted_index,documents

# Querying the Inverted Index
def query_inverted_index(word_list,inverted_index):
    try:
        inverted_word_list = [inverted_index[word] for word in word_list]
        #print(inverted_word_list)
    except KeyError:
        return [-1]
    if len(inverted_word_list)>0:
        return reduce(np.intersect1d,inverted_word_list)
    else:
        return [-1]

# Processing the Query and passing it for Inverted Index Query
def query(query,inverted_index,documents):
    query=preprocess_string(query)
    print(query)
    query = [word.lower() for word in query.split()]
    query = " ". join(query)
    word_list=tokenize(query)
    word_list=stopwords_removal(word_list)
    document_index_list = query_inverted_index(word_list,inverted_index)
    #print(document_index_list)
    #print ([documents[index] for index in document_index_list])
    if -1 not in document_index_list:
        return [documents[index] for index in document_index_list]
    else:
        return []
    
# Printing the results (For Debugging)
def display_results(query,results):
    print("Query:"+ query)
    if len(results) > 0:
        print(results)
    else:
        print("unanswerable")

# Retriving the results using the Query Function 
def retrieve(que):
    results = query(que, inverted_idx, documents)
    return(results)
    
# Preparing the Inverted Index 
inverted_idx, documents = index('Dataset.csv')

# Flaks app handeling the Search queries and the Front end
app = Flask(__name__)
app.secret_key = os.urandom(42)
app.config['PAGE_SIZE'] = 10
app.config['VISIBLE_PAGE_COUNT'] = 10
#app = Flask(static_folder='C:\\Users\\draithatha\\Documents\\Study\\BIA\\Flask\\Images')

@app.route('/')
def index():
    #page = int(request.args.get('page', 1))
    query = request.args.get("query", None)
    q = query
    
    if query:
        #app.logger.info("Query {} received".format(query))
        page = int(request.args.get('page', 1))
        #query = request.args.get("query", None)
        results = retrieve(query)
        
        if (len(results)>0):
            count = len(results)
            data = results
            pager = Pager(page, count)
            pages = pager.get_pages()
            skip = (page - 1) * current_app.config['PAGE_SIZE']
            limit = current_app.config['PAGE_SIZE']
            data_to_show = data[skip: skip + limit]
            #print(data_to_show)
            return render_template('results.html', pages=pages, query=query, data_to_show=data_to_show)
        else:
            return render_template('no_results.html', query=query)

    else:
        return render_template('index.html')
    
app.run()
