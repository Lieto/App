from flask import Flask, render_template
from collections import Counter
import os

UPLOAD_FOLDER = '/home/ubuntu/App/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    pass


@app.route('/')

def hello_world():
    return render_template('hello.html')

@app.route('/countme/<input_str>')

def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)



if __name__ == '__main__':
    app.run()

