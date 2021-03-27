import sqlite3
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
import random

lemmatizer = WordNetLemmatizer()
words = []
classes = []
documents = []
ignore_words = ['?', '!']

# Коннектим БД
connection = sqlite3.connect("ChatbotDB.db")
cursor = connection.cursor()
cursor.execute("SELECT patterns.text, tags.name "
               "FROM patterns INNER JOIN tags ON patterns.tag_id = tags.id")
patterns = cursor.fetchall()

# Токенизация - разбиение текста на слова
for pattern in patterns:
    w = nltk.word_tokenize(pattern[0])
    words.extend(w)
    documents.append((w, pattern[1]))
    if pattern[1] not in classes:
        classes.append(pattern[1])

# Лемматизация - приведение слов к нормальное форме
# Для существительных — именительный падеж, единственное число
# Для прилагательных — именительный падеж, единственное число, мужской род
# Для глаголов, причастий, деепричастий — глагол в инфинитиве несовершенного вида
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
# Сортируем тэги по алфавиту
classes = sorted(list(set(classes)))
# document = пара паттерн-тэг
print(len(documents), "documents")
# classes - это тэги
print(len(classes), "classes", classes)
# words = все уникальные слова из паттернов
print(len(words), "unique lemmatized words", words)
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Создаём тренировочные данные
training = []
# Пустой массив для вывода
output_empty = [0] * len(classes)
# Тренировочные данные, создаём мешок слов для каждого предложения
for doc in documents:
    # Инициализируем мешок слов
    bag = []
    # Список токенизированных слов для каждого паттерна
    pattern_words = doc[0]
    # Лемматизируем каждое слово - приводим к начальной форме, пытаясь определить однокоренные слова
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # Создаём мешок слов с единицей в конце списка, если найдено совпадение слова в текущем шаблоне
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    # В выводе будет 1 для подходящего тэга для каждого паттерна и 0 - для остальных
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])
# Перемешиваем всё и приводим к массиву numpy для удобства обучения сети
random.shuffle(training)
training = np.array(training)
# Создаём тренировочную и тестовую выборки. X - паттерны, Y - тэги
train_x = list(training[:, 0])
train_y = list(training[:, 1])
print("Training data created")

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
print("model created")
