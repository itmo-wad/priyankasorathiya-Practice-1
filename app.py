from flask import Flask, flash, render_template, request, url_for, redirect
from pymongo import MongoClient
import os.path
import random

upload_folder = "static/upload"
allowed_extensions = set(["jpg", "jpeg", "png", "gif"])


app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key= b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient('localhost', 27017)
db = client.practice
users = db.users
notebooks = db.notebooks
chats = db.chats


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            users.insert_one({'username': username, 'password': password})
        else:
            flash("No username or password given")
            return render_template('signup.html')
        return redirect(url_for('auth'))

    return render_template('signup.html')


@app.route('/auth', methods=('GET', 'POST'))
def auth():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user_found = users.find_one({'username': username, 'password': password})
        if user_found:
            return redirect(url_for('secret'))
        else:
            return render_template('auth.html', bad_login=True)

    return render_template('auth.html')

@app.route('/secret')
def secret():
    return render_template('secret.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method=='POST':
        if 'file' not in request.files:
            flash('No image uploaded')
            return render_template('upload.html')
        image = request.files['file']
        if image.filename == '':
            flash('No image uploaded')
            return render_template('upload.html')
        if image and allowed_file(image.filename):
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            return redirect(url_for('uploaded', filename=image.filename))
        else:
            flash('Wrong file extension')
            return render_template('upload.html')
    return render_template('upload.html')

@app.route('/uploaded/<filename>')
def uploaded(filename):
    if os.path.exists("static/upload/"+filename):
        return app.send_static_file("upload/" + filename)
    else:
        return redirect(url_for('upload'))

@app.route('/notebook', methods=('GET', 'POST'))
def notebook():
    if request.method=='POST':
        if "deleteAll" in request.form:
            notebooks.delete_many({})
        else:
            title = request.form['title']
            text = request.form['text']
            if title and text:
                notebooks.insert_one({'title': title, 'text': text})
            else:
                flash("No title or text given")

    listOfNotebooks = notebooks.find()
    return render_template('notebook.html', numberOfNotebooks = len(list(notebooks.find())), notebooks = listOfNotebooks)

def botResponse(message):
    greetings = ["hello", "hey", "good morning", "good evening", "hiya"]
    answers = ["I think so", "No absolutely not", "Maybe", "I don't know", "Possibly", "Yes and you ?", "Yes", "No"]
    response = "I am a bot"

    if message.lower() in greetings:
        response = "Hey!"
    if '?' in message:
        response = answers[random.randint(0,7)]

    return response

@app.route('/chatbot', methods=('GET', 'POST'))
def chatbot():
    if request.method=='POST':
        if "deleteAll" in request.form:
            chats.delete_many({})
        else:
            name = request.form['name']
            message = request.form['message']
            if name and message:
                chats.insert_one({'name': name, 'message': message})

                response = botResponse(message)
                chats.insert_one({'name': "Bot", 'message': response})

    listOfMessages = chats.find()
    return render_template('chatbot.html', messages = listOfMessages)

if __name__ == "__main__":
    app.run( debug=True)