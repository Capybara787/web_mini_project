import flask, os, sqlite3
from flask import render_template, request, redirect, url_for, session 
from flask import send_from_directory
from werkzeug.utils import secure_filename

import base64

# create a web application for a pet adoption page. 
# The page should have a login page, a page to register a new user, a page to list pets, add pets, edit pets and delete pets.
# To load the pets, read data from db.db file. 
# users should only be able to see index.html if they are logged in.

app = flask.Flask(__name__)
app.secret_key = 'batman'

conn = sqlite3.connect('db.db', check_same_thread=False)
c = conn.cursor()

@app.route('/')
def index():
    pets = c.execute("SELECT * from pets").fetchall()
    pet_images = c.execute("SELECT * from pet_images").fetchall()
    pet_images = pet_images[0][2:]
    for image in pet_images:
        image = base64.b64encode(image).decode('utf-8')
    return render_template('index.html', pets=pets, pet_images=pet_images)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password)).fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        contact = request.form['contact']
        existing_user = c.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        c.execute("INSERT INTO users (name, password, contact) VALUES (?, ?, ?)", (name, password, contact))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        sex = request.form['sex']
        age = request.form['age']
        fee = request.form['fee']
        description = request.form['description']
        image1 = request.files['image1'].read()
        image2 = request.files['image2'].read()
        image3 = request.files['image3'].read()
        # Save the images as blobs in the database
        c.execute("INSERT INTO pets (name, type, sex, age, fee, writeup, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (name, type, sex, age, fee, description, session['user_id']))
        c.execute("INSERT INTO pet_images (pet_id, image1, image2, image3) VALUES (?, ?, ?, ?)", (c.lastrowid, image1, image2, image3))
        # c.execute("INSERT INTO pet_images (pet_id, image1, image2, image3) VALUES (?, ?, ?, ?)", 
        #          (c.lastrowid, image1.filename, image2.filename, image3.filename))
        conn.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/interested/<int:pet_id>', methods=['GET', 'POST'])
def interested(pet_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        # Check if the user has already expressed interest in this pet
        existing_interest = c.execute("SELECT * FROM interested WHERE pet_id=? AND user_id=?", (pet_id, session['user_id'])).fetchone()
        if existing_interest:
            return render_template('interested.html', pet_id=pet_id, error='You have already expressed interest in this pet.')
        
        # Insert the new interest record into the database
        c.execute("INSERT INTO interested (pet_id, user_id) VALUES (?, ?)", (pet_id, session['user_id']))
        conn.commit()
        return redirect('/')
    
    # Fetch the pet information to display on the page
    pet = c.execute("SELECT * FROM pets WHERE id=?", (pet_id,)).fetchone()
    return render_template('interested.html', pet=pet)


if __name__ == '__main__':
    app.run(debug=True)

