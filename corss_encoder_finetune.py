# -*- coding: utf-8 -*-
"""corss-encoder-finetune.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15X2N4MtQGW4w46Mt4aAf2qHFIM0a1OU4
"""

import csv
import pickle

# !pip install pip install sentencepiece

# !pip install transformers

from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-distilroberta-base")

classifier.model.classifier.out_proj.out_features=6

classifier.model

for param in classifier.model.roberta.parameters():
  param.requires_grad = False

import os, psutil

def main():
    import time
    start_time = time.time()
    from transformers import pipeline
    import pandas as pd
    # from datasets import load_metric
    import numpy as np
    import math
    from sklearn.metrics import classification_report

    
    # classifier = pipeline("zero-shot-classification", model="microsoft/deberta-large-mnli") #GPU
    # classifier.model.classifier=nn.Linear(in_features=1024, out_features=6, bias=True)
    # classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")  # GPU
#     print('classifier taken')
    test_file = "/content/Topic Annotation - ROXANNE V2.csv"

    # define the topics here
    #candidate_labels = ['Drugs', 'Meeting', 'Money', 'Work Conversations', 'Family Conversations', 'Other']
    candidate_labels = ['Drugs', 'Work Conversations', 'Other', 'Family-Friend Conversations', 'Meeting', 'Money']

    predictions = []

    # Read the csv file for text
    
    header_list = ["id", "text", "topic"]
    # data = pd.read_csv(test_file, names=header_list)
    data = pd.read_csv(test_file, encoding="ISO-8859-1")

    filter_keys = ['labels']
    output = []
    # Iterate over the whole data and evaluate
#     print('before for loop')
    rows_to_write=['Call_ID','Transcript','Labels','Predicted Labels']
    with open('predicted.csv','w') as csvfile:
      csvwriter = csv.writer(csvfile)
      csvwriter.writerow(rows_to_write)      
      for index, row in data.iterrows():
          d = {}
          sequence = row["Transcript"]
          word_list = sequence.split()
          sequence_length = len(word_list)
          # print("sequence:",sequence)
          # print("Call_ID:",row["id"])
          # print("Sentence Length:",sequence_length)
          # result = classifier(sequence,candidate_labels,multi_label=True)
          result = classifier(sequence, candidate_labels,multi_label=True)
          labels = result['labels']
          scores = result['scores']
          pred_class = labels[np.argmax(scores)]

          #print("result:",result)
          #print(f'CALL_ID : {row["Call_ID"]} , PREDICTED_CLASS : {pred_class}')
          temp = list(map(result.get, filter_keys))
          d['text'] = row["Transcript"]
          d['topic'] = temp[0][0]
          #print(f'CALL_ID : {row["Call_ID"]} , PREDICTED_CLASS : {temp}')
          csvwriter.writerow([row["Call_ID"],row["Transcript"],row["Broad Topic[Drugs', 'Work Conversations', 'Other', 'Family-Friend Conversations', 'Money', 'Meeting']"],pred_class])
#           print(f'DONE {index}/{data.shape[0]}')
#       print("--- %s seconds ---" % (time.time() - start_time))


process = psutil.Process(main())
# print(process.memory_info().rss)

import pandas as pd

df=pd.read_csv('/content/predicted.csv')
df.head()

import numpy as np
df['Actual Labels']=np.empty((len(df), 0)).tolist()
df.head()

for i , row in df.iterrows():
  label=row['Labels']
  label=label.replace('Meeting Conversation','Meeting')
  label=label.split('|')
  df.at[i,'Actual Labels']=label

  label1=row['Predicted Labels']

  df.at[i,'Predicted Labels']=[label1]

y_true=df['Actual Labels'].to_list()
y_pred=df['Predicted Labels'].to_list()

y_true=np.asarray(y_true)
y_pred=np.asarray(y_pred)
total=['Drugs', 'Meeting','Family-Friend Conversations','Money','Work Conversations','Other']
true_pos=0
false_pos=0
false_neg=0
true_neg=0
for i in range(y_true.shape[0]):
  a=y_true[i]
  b=y_pred[i]
  tp=  len(np.intersect1d(a,b))
  fp = len(np.setdiff1d(b,a))
  fn=  len(np.setdiff1d(a,b))
  union=np.union1d(a,b)
  tn = len(np.setdiff1d(total,union))
  true_pos+=tp
  false_pos+=fp
  false_neg+=fn
  true_neg+=tn
precision=true_pos/(true_pos+false_pos)
recall=true_pos/(true_pos+false_neg)
f1=2*precision*recall/(precision+recall)
accuracy=(true_pos+true_neg)/(true_pos+true_neg+false_pos+false_neg)
