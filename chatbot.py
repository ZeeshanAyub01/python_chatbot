#Building a chatbot with NLP
import numpy as np
import tensorflow as tf
import re
import time
import os

lines = open('movie_lines.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')

id2line = {}

for line in lines:
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        id2line[_line[0]] = _line[4]
        
conversation_ids = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'","").replace(" ","")
    conversation_ids.append(_conversation.split(','))
    
questions = []
answers = []

for conversation in conversation_ids:
    for i in range(len(conversation) - 1):
        questions.append(id2line[conversation[i]])
        answers.append(id2line[conversation[i+1]])
        
def cleanText(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"there's", "there is", text)
    text = re.sub(r"when's", "when is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"[-()\"/@:;#~<>{}+=?.,|]", "", text)
    return text

#Clean the questions
clean_questions = []
for question in questions:
    clean_questions.append(cleanText(question))
    
#Clean the answers
clean_answers = []
for answer in answers:
    clean_answers.append(cleanText(answer))
    
#Creating a dictionary that maps each word to its number of occurences
word2count = {}
for question in clean_questions:
    for word in question.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
    
for answer in clean_answers:
    for word in answer.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
            
#Creating two dictionaries that map the questions words and the answers words to n unique integers
threshold = 20 #Can experiment with a lower value here if computer is fast enough
questionswords2int = {}
word_number = 0

for word,count in word2count.items():
    if count >= threshold:
        questionswords2int[word] = word_number
        word_number += 1
        
answerswords2int = {}
word_number = 0

for word,count in word2count.items():
    if count >= threshold:
        answerswords2int[word] = word_number
        word_number += 1

#Add the last tokens to these two dictionaries we created
tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']

for token in tokens:
    questionswords2int[token] = len(questionswords2int) + 1 
for token in tokens:
    answerswords2int[token] = len(answerswords2int) + 1
 
#Creating the inverse dictionary of the answerswords2int dictionary    
answersints2words = {w_i: w for w, w_i in answerswords2int.items()}

#Adding the End of String token to the end of every answer
for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>'
    
#Translating all the questions and the answers into integers
# and replacing all the words that were filtered out by <OUT>
questions_into_int = []
for question in clean_questions:
    ints = []
    for word in question.split():
        if word not in questionswords2int:
            ints.append(questionswords2int['<OUT>'])
        else:
            ints.append(questionswords2int[word])
        questions_into_int.append(ints)

answers_into_int = []
for answer in clean_answers:
    ints = []
    for word in answer.split():
        if word not in answerswords2int:
            ints.append(answerswords2int['<OUT>'])
        else:
            ints.append(answerswords2int[word])
        answers_into_int.append(ints)
        
#Sorting the questions and answers, both by the legnth of the questions
#This is done to speed up training and to minimize losses
sorted_clean_questions = []
sorted_clean_answers = []

for length in range(1, 25 + 1): # + 1, because upper bounds in Python are not included
    for i in enumerate(questions_into_int):
        if len(i[1]) == length:
            sorted_clean_questions.append(questions_into_int[i[0]])
            sorted_clean_answers.append(answers_into_int[i[0]])
        