import sqlite3
import nltk
import pymorphy2
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
import random
import string

morph = pymorphy2.MorphAnalyzer()
# words = все уникальные слова из паттернов
words = []
# classes - это тэги
classes = []
# document = пара паттерн-тэг
documents = []
ignore_words = list(string.punctuation)

# Коннектим БД
connection = sqlite3.connect("ChatbotDB.db")
cursor = connection.cursor()
cursor.execute("SELECT patterns.text, tags.name "
               "FROM patterns INNER JOIN tags ON patterns.tag_id = tags.id")
patterns = cursor.fetchall()

# Токенизация - разбиение текста на слова
for pattern in patterns:
    word = nltk.word_tokenize(pattern[0], language="russian")
    words.extend(word)
    documents.append((word, pattern[1]))
    if pattern[1] not in classes:
        classes.append(pattern[1])

# Лемматизация - приведение слов к нормальное форме
# Для существительных — именительный падеж, единственное число
# Для прилагательных — именительный падеж, единственное число, мужской род
# Для глаголов, причастий, деепричастий — глагол в инфинитиве несовершенного вида
words = [morph.parse(word.lower())[0].normal_form for word in words
         if not (word.lower() in ignore_words or word.isdigit())]
# Сортируем слова по алфавиту и убираем повторяющиеся
words = sorted(list(set(words)))
# Сортируем тэги по алфавиту и убираем повторяющиеся
classes = sorted(list(set(classes)))
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Создаём тренировочные данные
training = []
# Пустой массив для вывода
output_empty = [0] * len(classes)
# Тренировочные данные, создаём мешок слов для каждого предложения
for document in documents:
    # Инициализируем мешок слов
    bag = []
    # Список токенизированных слов для каждого паттерна
    pattern_words = document[0]
    # Лемматизируем каждое слово - приводим к начальной форме, пытаясь определить однокоренные слова
    pattern_words = [morph.parse(word.lower())[0].normal_form for word in pattern_words]
    # Создаём мешок слов с единицей в конце списка, если найдено совпадение слова в текущем шаблоне
    for word in words:
        bag.append(1) if word in pattern_words else bag.append(0)
    # В выводе будет 1 для подходящего тэга для каждого паттерна и 0 - для остальных
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])
# Перемешиваем всё и приводим к массиву numpy для удобства обучения сети
random.shuffle(training)
training = np.array(training)
# Создаём тренировочную и тестовую выборки. X - паттерны, Y - тэги
train_x = list(training[:, 0])
train_y = list(training[:, 1])

# Создаём нейронную модель с 3 слоями. Первый слой содержит 128 нейронов, второй - 64 нейрона,
# 3-й слой содержит количество нейронов, равное количеству тэгов, для предсказания итогового тэга, используя softmax
# Softmax - это математическая функция, которая преобразует вектор чисел в вектор вероятностей, где вероятности каждого
# Значения пропорциональны относительному масштабу каждого значения в векторе
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))
# Компилируем модель
# Стохастический градиентный спуск с ускоренным градиентом Нестерова даёт хорошие результаты для этой модели.
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
# Тренируем модель и сохраняем её
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)
