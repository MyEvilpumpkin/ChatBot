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
    # Токенизируем паттерны
    sentence_words = nltk.word_tokenize(sentence)
    # Приводим слова к начальной форме
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# Функция возвращает массив, который является мешком слов: 0 или 1 для каждого слова в мешке, которое есть в предложении

def bow(sentence, words, show_details=True):
    # Токенизируем паттерн
    sentence_words = clean_up_sentence(sentence)
    # Мешок слов - набор уникальных слов в предложении
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # Присвоить 1, если текущее слово есть в словаре
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # Отбрасываем прогнозы ниже порогового значения
    p = bow(sentence, loaded_words, show_details=False)
    res = model.predict(np.array([p]))[0]
    error_threshold = 0.9
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    # Сортируем по вероятности
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": loaded_classes[r[0]], "probability": str(r[1])})
    if not results:
        return_list.append({"intent": "noanswer", "probability": str(error_threshold)})
    return return_list


def get_response(ints):
    connection = sqlite3.connect("ChatbotDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT responses.response_text "
                   "FROM responses INNER JOIN tags ON responses.tag_id = tags.tag_id "
                   "AND tags.tag_name = \"%tag_name\"".replace("%tag_name", ints[0]['intent']))
    responses = cursor.fetchall()

    cursor.execute("SELECT commands.command_name "
                   "FROM commands INNER JOIN tags ON commands.tag_id = tags.tag_id "
                   "AND tags.tag_name = \"%tag_name\"".replace("%tag_name", ints[0]['intent']))
    commands = cursor.fetchall()

    result = (random.choice(responses)[0], commands)
    return result


def chatbot_response(msg):
    ints = predict_class(msg, loaded_model)
    result = get_response(ints)
    return result
