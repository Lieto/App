from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g
from werkzeug.utils import secure_filename

from collections import Counter
import os
import subprocess
import sqlite3
import time
import logging

UPLOAD_FOLDER = '/home/ubuntu/App/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
DATABASE = '/var/www/html/App/bart.db'

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)

    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def run_nn(style_image, original_image):
    os.chdir('/home/ubuntu/Deepstyle/neural-style')
    args = ['th',
            'neural_style.lua',
            '-style_image',
            style_image,
            '-content_image',
            original_image,
            ]
    result = subprocess.check_output(args)

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM natpark""")
    return  '<br>'.join(str(row) for row in rows)

@app.route("/state/<state>")
def sortby(state):
    rows = execute_query("""SELECT * FROM natpark WHERE state = ?""", [state.title()])
    return '<br>'.join(str(row) for row in rows)


@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route("/print_data/")
def print_data():

    start_time = time.time()
    cur = get_db().cursor()
    try:
        minute_of_day = int(request.args.get('time'))
    except ValueError:
        return "Time must be an integer"
    station = request.args.get('station')
    print(minute_of_day)
    day = request.args.get('day')
    dest = request.args.get('dest')
    result = execute_query(
        """SELECT etd, count(*)
           FROM etd
           WHERE dest = ? AND minute_of_day = ?
               AND station = ? AND day_of_week = ?
            GROUTP BY etd""",
        (dest, minute_of_day, station, day)
    )
    str_rows = [','.join(map(str, row)) for row in result]
    query_time = time.time() - start_time
    logging.info("executed query in %s" % query_time)
    cur.close()
    header = 'etd,count\n'
    return header + '\n'.join(str_rows)

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            #flash('No filepart')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #Do nn stuff...
            style_file = os.path.join('/home/ubuntu/Deepstyle/neural-style/examples/inputs', 'picasso_selfport1907.jpg')
            original_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            run_nn(style_file, original_file)
            outfile = 'out.png'
            return redirect(url_for('uploaded_file', filename=outfile))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/home/ubuntu/Deepstyle/neural-style',
                               filename)

@app.route('/show_result')
def show_result():
    return send_from_directory(app.config['UPLOAD_FOLDER'],'out.png')

@app.route('/countme/<input_str>')

def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)


if __name__ == '__main__':
    app.run(debug=True)

