import flask, os, sqlite3
from flask import render_template, request, redirect, url_for, session
from flask import send_from_directory
from werkzeug.utils import secure_filename

import base64

app = flask.Flask(__name__)
app.secret_key = 'batman'

conn = sqlite3.connect('db.db', check_same_thread=False)
c = conn.cursor()

@app.route('/')
def index():
    pets = c.execute("SELECT * from pets").fetchall()
    pet_images = c.execute("SELECT * from pet_images").fetchall()
    print(pet_images)
    username = c.execute("SELECT name from users WHERE id=?", (session.get('user_id'),)).fetchone()[0] if 'user_id' in session else None
    print(username)
    return render_template('index.html', pets=pets, pet_images=pet_images, username=username)

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
        image1 = request.files['image1']
        image2 = request.files['image2']
        image3 = request.files['image3']
        c.execute("INSERT INTO pets (name, type, sex, age, fee, writeup, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (name, type, sex, age, fee, description, session['user_id']))
                
        # create a new folder with pet_id as folder name and upload image1, image2, image3 to that folder
        os.mkdir('static/images/' + str(c.lastrowid))
        image1.save('static/images/' + str(c.lastrowid) + '/image1.jpg')
        image2.save('static/images/' + str(c.lastrowid) + '/image2.jpg')
        image3.save('static/images/' + str(c.lastrowid) + '/image3.jpg')

        # save the image paths in the database
        c.execute("INSERT INTO pet_images (pet_id, image1, image2, image3) VALUES (?, ?, ?, ?)", 
                  (c.lastrowid, 'static/images/' + str(c.lastrowid) + '/image1.jpg', 
                   'static/images/' + str(c.lastrowid) + '/image2.jpg', 
                   'static/images/' + str(c.lastrowid) + '/image3.jpg'))
        conn.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/interested/<int:pet_id>', methods=['GET', 'POST'])
def interested(pet_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    pet = c.execute("SELECT * FROM pets WHERE id=?", (pet_id,)).fetchall()[0]
    if request.method == 'POST':
        # Check if the user has already expressed interest in this pet
        existing_interest = c.execute("SELECT * FROM interested_users WHERE pet_id=? AND users_id=?", (pet_id, session['user_id'])).fetchone()
        if existing_interest:
            return render_template('interested.html',pet=pet, pet_id=pet_id, error='You have already expressed interest in this pet.')
        
        # Insert the new interest record into the database
        c.execute("INSERT INTO interested_users (pet_id, users_id) VALUES (?, ?)", (pet_id, session['user_id']))
        conn.commit()
        return redirect('/')
    
    # Fetch the pet information to display on the page
    return render_template('interested.html', pet=pet)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/my_pets')
def my_pets():
    if 'user_id' not in session:
        return redirect('/login')
    pets = c.execute("SELECT * from pets WHERE owner_id=?", (session['user_id'],)).fetchall()
    interested_users = c.execute("SELECT * from interested_users WHERE users_id=?", (session['user_id'],)).fetchall()
    return render_template('my_pets.html', pets=pets, interested_users=interested_users)


if __name__ == '__main__':
    app.run(debug=True)

