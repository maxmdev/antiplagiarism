# -*- coding: utf-8 -*-

import fnmatch
import fulltext
import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug import SharedDataMiddleware
import re
import math
import time
import json
import shinglmethods
import shinglmethods_sorted
import cosine
import moodlemethod
import levensteinmethod

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx', 'odt'])

app = Flask("__name__")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def database_files():
    list_files = []
    for root, dir, files in os.walk("./uploads"):
        for items in fnmatch.filter(files, "*.doc") + fnmatch.filter(files,"*.docx") +fnmatch.filter(files, ".txt"):
            list_files.append(items)
    print(list_files)
    return list_files

q = ""

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/txt/<path:path>')
def send_txt(path):
    return send_from_directory('txt', path)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            str_data = []
            t = database_files()
            for k in t:
                text_from_file = ""
                try:
                    text_from_file = fulltext.get('uploads/' + str(k), None).replace('\n', ' ').replace('\"', "").replace("\'", "")
                except:
                    continue
                cosine_freq = cosine.cosinedatabaseTF(text_from_file)
                shingles = []
                for i in range(1,4):
                    shingle = "{" + shinglmethods.genshingle_n(text_from_file, i) + "}"
                    shingles.append(shingle)
                shingle_t = "\"shingles_by_id\": [" + ",".join(shingles) + "]"
                shingles_sorted = []
                for i in range(1,4):
                    shingle_sorted = "{" + shinglmethods.genshingle_n(text_from_file, i) + "}"
                    shingles_sorted.append(shingle_sorted)
                shingle_t_sorted = "\"shingles_sorted_by_id\": [" + ",".join(shingles) + "]"
                moodles = []
                for i in range(1,4):
                    moodle = "{" + moodlemethod.genmoodle_n(text_from_file, i) + "}"
                    moodles.append(moodle)
                moodle_t = "\"moodles_by_id\": [" + ",".join(moodles) + "]"
                filepath = "txt/" + str(k).replace("doc", "").replace("docx", "").replace("txt", "") + "txt"
                hs = open(filepath, "w")
                str_data.append("{" + "\"name\":\"{}\", \"filepath\":\"{}\", {}, {}, {}, {}".format(str(k), filepath, cosine_freq, shingle_t, shingle_t_sorted, moodle_t) + "}")
                hs.write(text_from_file)
                hs.close()
            text_for_json = ",".join(str_data)
            hj = open("database.json", "w")
            hj.write("[" + text_for_json + "]")
            hj.close()

            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file_for_check():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('/tmp', filename))
            text = fulltext.get('/tmp/' + filename)
            #return text
            return render_template('index.html', query=text)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route("/", methods=['GET'])
def loadPage():
    return render_template('index.html', query="")

@app.route("/json", methods=['GET'])
def loadPagerrr():
    a = "{\"id\": 1}"
    return jsonify(a)

@app.route("/", methods=['POST'])
def parser():
    with open('database.json') as json_file:
        database = json.load(json_file)
        for p in database:
            print (p['name'])
    print(request.form)
    inputQuery = request.form['query']
    #inputQuery = re.sub(r'[?|$|.|!|:|;|"| ]', r'', inputQuery)
    select_method = request.form['select']
    stopunion = ''
    stoppretext = ''
    try:
        stopunion = request.form['stop-union']
    except:
        pass
    try:
        stoppretext = request.form['stop-pretext']
    except:
        pass

    if select_method == "frequency-cosine":
        file_most_simular = ''
        matchPercentage = 0
        cosine_mean_len_words_total = 0
        total_time = 0
        count_iter_total = 0
        with open("/tmp/input.txt", "w+") as input:
            input.write(inputQuery)
        for k in database:
            time_start = time.time()
            with open(k['filepath']) as fdatabase:
                ftext_from_database = fdatabase.read()
            matchPercentage_test, count_iter, cosine_mean_len_words = cosine.cosineSimilarity(inputQuery, ftext_from_database)
            count_iter_total += count_iter
            cosine_mean_len_words_total += cosine_mean_len_words
            print (k['name'], matchPercentage_test)
            if matchPercentage_test > matchPercentage:
                matchPercentage = matchPercentage_test
                file_most_simular = k['name']
                filepath_most_simular = k['filepath']
            time_opetation = time.time() - time_start
            print (time_opetation)
            total_time += time_opetation
        print ("            ======================================================")
        print ("            =============== СТАТИСТИКА ===========================")
        print ("            Общее время операции по методу частоты {} секунд.".format(total_time))
        print ("            Кол-во файлов в БД {} файлов".format(len(database)))
        print ("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
        print("            средняя длина слов в файлах БД - {} слов".format(cosine_mean_len_words_total/len(database)))
        print ("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
        print("            ======================================================\n")
        output = "%0.02f%%"%matchPercentage
        dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format("/tmp/input.txt", filepath_most_simular, output, file_most_simular)
        dict_array = '{' + dict_array + '}'
        print (dict_array)
        return jsonify(dict_array)


    if select_method == "basic-shingl":
        #fd = open("database.txt", "r")

        if stopunion == "" and stoppretext == "":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print ("FTEXT ",ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods.return_sim_procents(inputQuery, ftext_from_database, "")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму шинглов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%"%matchPercentage
            print ("Со всеми stop словами")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)
        if stopunion == "checked" and stoppretext == "":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print("FTEXT ", ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods.return_sim_procents(inputQuery, ftext_from_database, "union")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму шинглов без союзов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(
                basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%" % matchPercentage
            print ("Без союзов")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)
        if stopunion == "" and stoppretext == "checked":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print("FTEXT ", ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods.return_sim_procents(
                    inputQuery, ftext_from_database, "pretext")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму шинглов без предлогов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(
                basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%"%matchPercentage
            print ("Без предлогов")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)

    if select_method == "sorted-shingl":
        #fd = open("database.txt", "r")

        if stopunion == "" and stoppretext == "":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print ("FTEXT ",ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods_sorted.return_sim_procents(inputQuery, ftext_from_database, "")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму отсортированных шинглов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%"%matchPercentage
            print ("Со всеми stop словами")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)
        if stopunion == "checked" and stoppretext == "":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print("FTEXT ", ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods_sorted.return_sim_procents(inputQuery, ftext_from_database, "union")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму отсортированных шинглов без союзов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(
                basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%" % matchPercentage
            print ("Без союзов")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)
        if stopunion == "" and stoppretext == "checked":
            file_most_simular = ''
            matchPercentage = 0
            basic_shingl_mean_len_words_total = 0
            total_time = 0
            count_iter_total = 0
            with open("/tmp/input.txt", "w+") as input:
                input.write(inputQuery)
            for k in database:
                time_start = time.time()
                with open(k['filepath']) as fdatabase:
                    ftext_from_database = fdatabase.read()
                    print("FTEXT ", ftext_from_database)
                matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods_sorted.return_sim_procents(
                    inputQuery, ftext_from_database, "pretext")
                count_iter_total += count_iter
                basic_shingl_mean_len_words_total += basic_shingl_mean_len_words
                if matchPercentage_test > matchPercentage:
                    matchPercentage = matchPercentage_test
                    file_most_simular = k['name']
                    filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
            print("            ======================================================")
            print("            =============== СТАТИСТИКА ===========================")
            print("            Общее время операции по алгоритму отсортированных шинглов без предлогов {} секунд.".format(total_time))
            print("            Кол-во файлов в БД {} файлов".format(len(database)))
            print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
            print("            средняя длина шинглов в файлах БД - {} шинглов".format(
                basic_shingl_mean_len_words_total / len(database)))
            print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
            print("            ======================================================\n")
            output = "%0.02f%%"%matchPercentage
            print ("Без предлогов")
            dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
                "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
            dict_array = '{' + dict_array + '}'
            print(dict_array)
            return jsonify(dict_array)

    if select_method == "moodle-crot":
        moodle_mean_len_words_total = 0
        total_time = 0
        count_iter_total = 0
        file_most_simular = ''
        matchPercentage = 0
        with open("/tmp/input.txt", "w+") as input:
            input.write(inputQuery)
        for k in database:
            time_start = time.time()
            with open(k['filepath']) as fdatabase:
                ftext_from_database = fdatabase.read()
            matchPercentage_test, count_iter, moodle_mean_len_words = moodlemethod.return_sim_procents(inputQuery, ftext_from_database)
            count_iter_total += count_iter
            moodle_mean_len_words_total += moodle_mean_len_words
            if matchPercentage_test > matchPercentage:
                matchPercentage = matchPercentage_test
                file_most_simular = k['name']
                filepath_most_simular = k['filepath']
                time_opetation = time.time() - time_start
                total_time += time_opetation
        print("            ======================================================")
        print("            =============== СТАТИСТИКА ===========================")
        print("            Общее время операции по алгоритму Moodle Crot {} секунд.".format(total_time))
        print("            Кол-во файлов в БД {} файлов".format(len(database)))
        print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
        print("            средняя длина рядов Moodle в файлах БД - {} порядков по 3 символа".format(
                moodle_mean_len_words_total / len(database)))
        print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
        print("            ======================================================\n")
        output = "%0.02f%%"%matchPercentage
        dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
            "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
        dict_array = '{' + dict_array + '}'
        print (dict_array)
        return jsonify(dict_array)

    if select_method == "levenshtein":
        levenstein_len_words_total = 0
        total_time = 0
        count_iter_total = 0
        file_most_simular = ''
        matchPercentage = 0
        with open("/tmp/input.txt", "w+") as input:
            input.write(inputQuery)
        for k in database:
            time_start = time.time()
            with open(k['filepath']) as fdatabase:
                ftext_from_database = fdatabase.read()
            matchPercentage_test, count_iter, levenstein_len_words = levensteinmethod.return_sim_procents(inputQuery, ftext_from_database)
            count_iter_total += count_iter
            levenstein_len_words_total += levenstein_len_words
            if matchPercentage_test > matchPercentage:
                matchPercentage = matchPercentage_test
                file_most_simular = k['name']
                filepath_most_simular = k['filepath']

                time_opetation = time.time() - time_start
                total_time += time_opetation
        print("            ======================================================")
        print("            =============== СТАТИСТИКА ===========================")
        print("            Общее время операции по алгоритму растояния Левенштейна {} секунд.".format(total_time))
        print("            Кол-во файлов в БД {} файлов".format(len(database)))
        print("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
        print("            средняя длина сравниваемых строк в файлах БД - {} строк".format(
                levenstein_len_words_total / len(database)))
        print("            Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
        print("            ======================================================\n")
        output = "%0.02f%%"%matchPercentage
        dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
            "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
        dict_array = '{' + dict_array + '}'
        print (dict_array)
        return jsonify(dict_array)


    if select_method == "complex":
        file_most_simular = ''
        filepath_most_simular = ''
        n = 0
        matchPercentage_sum = 0
        max_of_methods = 0
        matchPercentage_cosine = 0
        matchPercentage_single = 0
        matchPercentage_single_sorted = 0
        matchPercentage_moodle = 0
        matchPercentage_levenstein = 0
        with open("/tmp/input.txt", "w+") as input:
            input.write(inputQuery)
        cosine_mean_len_words_total = 0
        total_time = 0
        count_iter_total = 0
        for k in database:
            time_start = time.time()
            with open(k['filepath']) as fdatabase:
                ftext_from_database = fdatabase.read()
            matchPercentage_test, count_iter, cosine_mean_len_words = cosine.cosineSimilarity(inputQuery,
                                                                                              ftext_from_database)
            count_iter_total += count_iter
            cosine_mean_len_words_total += cosine_mean_len_words
            if matchPercentage_test > matchPercentage_cosine:
                matchPercentage_cosine = matchPercentage_test
                file_most_simular_cosine = k['name']
                filepath_most_simular_cosine = k['filepath']
            if int(matchPercentage_cosine) != 0:
                matchPercentage_sum += matchPercentage_cosine
                if max_of_methods < matchPercentage_cosine:
                    max_of_methods = matchPercentage_cosine
                    file_most_simular = file_most_simular_cosine
                    filepath_most_simular = filepath_most_simular_cosine
                n += 1
            time_opetation = time.time() - time_start
            total_time += time_opetation

            matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods.return_sim_procents(inputQuery, ftext_from_database, "")
            if matchPercentage_test > matchPercentage_single:
                matchPercentage_single = matchPercentage_test
                file_most_simular_shingl = k['name']
                filepath_most_simular_shingl = k['filepath']
            if int(matchPercentage_single) != 0:
                matchPercentage_sum += matchPercentage_single
                if max_of_methods < matchPercentage_single:
                    max_of_methods = matchPercentage_single
                    file_most_simular = file_most_simular_shingl
                    filepath_most_simular = filepath_most_simular_shingl
                n += 1
            time_opetation = time.time() - time_start
            total_time += time_opetation

            matchPercentage_test, count_iter, basic_shingl_mean_len_words = shinglmethods_sorted.return_sim_procents(inputQuery, ftext_from_database, "")
            if matchPercentage_test > matchPercentage_single_sorted:
                matchPercentage_single_sorted = matchPercentage_test
                file_most_simular_single_sorted = k['name']
                filepath_most_simular_shingl_sorted = k['filepath']
            if int(matchPercentage_single_sorted) != 0:
                matchPercentage_sum += matchPercentage_single_sorted
                if max_of_methods < matchPercentage_single_sorted:
                    max_of_methods = matchPercentage_single_sorted
                    file_most_simular = file_most_simular_single_sorted
                    filepath_most_simular = filepath_most_simular_shingl_sorted
                n += 1
            time_opetation = time.time() - time_start
            total_time += time_opetation


            matchPercentage_test, count_iter, moodle_mean_len_words = moodlemethod.return_sim_procents(inputQuery, ftext_from_database)
            if matchPercentage_test > matchPercentage_moodle:
                matchPercentage_moodle = matchPercentage_test
                file_most_simular_moodle = k['name']
                filepath_most_simular_moodle = k['filepath']
            if int(matchPercentage_moodle) != 0:
                matchPercentage_sum += matchPercentage_moodle
                if max_of_methods < matchPercentage_moodle:
                    max_of_methods = matchPercentage_moodle
                    file_most_simular = file_most_simular_moodle
                    filepath_most_simular = filepath_most_simular_moodle
                n += 1
            time_opetation = time.time() - time_start
            total_time += time_opetation

            matchPercentage_test, count_iter, levenstein_len_words = levensteinmethod.return_sim_procents(inputQuery, ftext_from_database)
            if matchPercentage_test > matchPercentage_levenstein:
                matchPercentage_levenstein = matchPercentage_test
                file_most_simular_levenstein = k['name']
                filepath_most_simular_levenstein = k['filepath']
            if int(matchPercentage_levenstein) != 0:
                matchPercentage_sum += matchPercentage_levenstein
                if max_of_methods < matchPercentage_levenstein:
                    max_of_methods = matchPercentage_levenstein
                    file_most_simular = file_most_simular_levenstein
                    filepath_most_simular = filepath_most_simular_levenstein
                n += 1
            time_opetation = time.time() - time_start
            total_time += time_opetation

        matchPercentage = float(matchPercentage_sum/n)

        print ("            ======================================================")
        print ("            =============== СТАТИСТИКА ===========================")
        print ("            Общее время операции по комплексному методу {} секунд.".format(total_time))
        print ("            Кол-во файлов в БД {} файлов".format(len(database)))
        print ("            Кол-во операций по алгоритму - {} операций".format(count_iter_total))
        print("             Наибольшее совпадение с файлом {} процент схожести {}".format(file_most_simular, matchPercentage))
        print("             ======================================================\n")
        output = "%0.02f%%"%matchPercentage
        dict_array = '"filepath_input": \"{}\", "filepath_most_simular":\"{}\", "output": \"{}\", "filename": \"{}\"'.format(
            "/tmp/input.txt", filepath_most_simular, output, file_most_simular)
        dict_array = '{' + dict_array + '}'
        print (dict_array)
        return jsonify(dict_array)

app.run(port=5000)

