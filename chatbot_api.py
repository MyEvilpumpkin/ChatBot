import sqlite3
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import random

lemmatizer = WordNetLemmatizer()
loaded_model = load_model('chatbot_model.h5')
loaded_words = pickle.load(open('words.pkl', 'rb'))
loaded_classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, loaded_words, show_details=False)
    res = model.predict(np.array([p]))[0]
    error_threshold = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": loaded_classes[r[0]], "probability": str(r[1])})
    return return_list


def get_response(ints):
    connection = sqlite3.connect("ChatbotDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT responses.response_text "
                   "FROM responses INNER JOIN tags ON responses.tag_id = tags.tag_id "
                   "AND tags.tag_name = \"%tag_name\"".replace("%tag_name", ints[0]['intent']))
    responses = cursor.fetchall()
    result = random.choice(responses)[0]
    return result


def chatbot_response(msg):
    ints = predict_class(msg, loaded_model)
    result = get_response(ints)
    return result
