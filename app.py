from flask import Flask, request, render_template, redirect, url_for, session, abort
import os
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'

db = SQLAlchemy(app)

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None  # Initialize error message
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_results.xls')

    # ✅ Ensure the results file exists before login
    if not os.path.exists(file_path):
        error_message = "Results file not uploaded yet. Please contact admin."
        return render_template('login.html', error_message=error_message)

    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        
        df = pd.read_excel(file_path)

        user_data = df[df['ID'] == user_id]
        if user_data.empty:
            error_message = "Invalid User ID. Please try again."
        elif user_data['Password'].values[0] != password:
            error_message = "Incorrect Password. Please try again."
        else:
            session['user_id'] = user_id
            return redirect(url_for('result'))

    return render_template('login.html', error_message=error_message)

@app.route('/result', methods=['GET'])
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_results.xls')

    # ✅ Ensure the results file exists before fetching results
    if not os.path.exists(file_path):
        return "Results file not found. Please contact admin."

    user_id = session['user_id']
    df = pd.read_excel(file_path)
    user_result = df[df['ID'] == user_id]

    if not user_result.empty:
        result_data = user_result.iloc[0]
        return render_template('result.html', user_id=user_id, result_data=result_data)
    else:
        return "Result not found."

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        # ✅ Ensure the uploads folder exists before saving the file
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'sample_results.xls'))
        return "File uploaded successfully!"

    return render_template('admin.html')

@app.route('/marks_to_grade.html')
def marks_to_grade():
    return render_template('marks_to_grade.html')

@app.route('/web_team.html')
def web_team():
    return render_template('web_team.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/convo.html')
def convo():
    return render_template('convo.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
