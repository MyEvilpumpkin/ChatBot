import sqlite3
import nltk
import pymorphy2
import pickle
import numpy as np
from keras.models import load_model
import random

morph = pymorphy2.MorphAnalyzer()
loaded_model = load_model('chatbot_model.h5')
loaded_words = pickle.load(open('words.pkl', 'rb'))
loaded_classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    # Токенизируем паттерны
    sentence_words = nltk.word_tokenize(sentence, language="russian")
    # Приводим слова к начальной форме
    sentence_words = [morph.parse(word.lower())[0].normal_form for word in sentence_words]
    return sentence_words


# Функция возвращает массив, который является мешком слов: 0 или 1 для каждого слова в мешке, которое есть в предложении

def bow(sentence, words):
    # Токенизируем паттерн
    sentence_words = clean_up_sentence(sentence)
    # Мешок слов - набор уникальных слов в предложении
    bag = [0] * len(words)
    for sentence_word in sentence_words:
        for i, word in enumerate(words):
            if word == sentence_word:
                # Присвоить 1, если текущее слово есть в словаре
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence, model):
    # Отбрасываем прогнозы ниже порогового значения
    prediction_data = bow(sentence, loaded_words)
    prediction_result = model.predict(np.array([prediction_data]))[0]
    error_threshold = 0.9
    results = [[i, result] for i, result in enumerate(prediction_result) if result > error_threshold]
    # Сортируем по вероятности
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for result in results:
        return_list.append({"intent": loaded_classes[result[0]], "probability": str(result[1])})
    if not results:
        return_list.append({"intent": "noanswer", "probability": str(error_threshold)})
    return return_list


def get_response(ints):
    connection = sqlite3.connect("ChatbotDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT responses.text "
                   "FROM responses INNER JOIN tags ON responses.tag_id = tags.id "
                   "AND tags.name = \"%tag_name\"".replace("%tag_name", ints[0]['intent']))
    responses = cursor.fetchall()
    cursor.execute("SELECT commands.name "
                   "FROM commands INNER JOIN tags ON commands.tag_id = tags.id "
                   "AND tags.name = \"%tag_name\"".replace("%tag_name", ints[0]['intent']))
    commands = cursor.fetchall()
    result = (random.choice(responses)[0], commands)
    return result


def chatbot_response(msg):
    ints = predict_class(msg, loaded_model)
    result = get_response(ints)
    return result
