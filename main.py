import sqlite3
import requests
from fake_useragent import UserAgent

db = sqlite3.connect('word.db')
cursor = db.cursor()
headers = {'user-agent': UserAgent().random}

# cursor.execute(f'''
#                 CREATE TABLE "word" IF NOT EXISTS  (
#                     "word_en" varchar(127) NOT NULL,
#                     "count_word" INTEGER NOT NULL,
#                     PRIMARY KEY("word_en")
#                 )'''
# )


def write_translet(words_list, examples_list, word, wrod_ru, c_word):
    result = (word, wrod_ru, c_word, words_list, examples_list)
    cursor.execute('INSERT INTO word VALUES(?, ?, ?, ?, ?)', result)


def get_translation(word, c_word):
    url = f'https://dictionary.yandex.net/dicservice.json/queryCorpus?sid=9956a209.61fff388.53ffaac5.74722d74657874&ui=ru&srv=tr-text&text={word}&type&lang=en-ru&flags=1063&src={word}&dst&chunks=1&maxlen=200&v=2&yu=3802167821631552752&yum=1631552753719681766'
    response = requests.get(url=url, headers=headers)
    data = response.json().get('result')
    words = ''
    examples = ''
    wrod_ru = ''

    # Перевод слова
    translet_word = data.get('tabs')
    c = 5 if len(translet_word) > 5 else len(translet_word)
    for i in range(c):
        word_translite = translet_word[i].get('translation').get('text')
        if word_translite:
            if i == 0:
                wrod_ru += word_translite
            words += word_translite
            words += ' | '
    # Пример фраз
    examples_line = data.get('examples')
    c = 5 if len(examples_line) > 5 else len(examples_line)
    for i in range(c):
        quote = examples_line[i].get('dst')
        translation_quote = examples_line[i].get('src')
        if quote and translation_quote:
            examples += quote + '\n' + translation_quote
            examples += ' | '

    write_translet(words, examples, word, wrod_ru, c_word)


def one_line(dict_, count, line):
    line = line.strip().lower().split()
    if line:
        for word in line:
            if (word.isalpha()) and (len(word) > 2):
                dict_[word] = dict_.setdefault(word, 0) +1
        count += 1
    return dict_, count

def write_db(dic):
    for key, val in dic.items():
        cursor.execute(f'SELECT count_word FROM word WHERE word_en = "{key}"')
        sum_ = cursor.fetchone()
        if sum_:
            cursor.execute(f'UPDATE word SET count_word = {val + sum_[0]} WHERE word_en = "{key}"')
        else:
            get_translation(key, val)
    db.commit()

def create_dict():
    book = 'Learning_Python.txt'
    dict_ = {}
    with open(book, 'r', encoding="utf-8") as file:
        count = 0
        for line in file:
            dict_, count = one_line(dict_, count, line)
            if count %1000 == 0:
                write_db(dict_)
                print(count)
        write_db(dict_)

if __name__ == '__main__':
    create_dict()
    db.close()