from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from werkzeug.security import check_password_hash
from PIL import Image
import os
import io
import time

app = Flask(__name__)
app.secret_key = 'clave-secreta-super-random'
UPLOAD_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PASSWORD_HASH = 'scrypt:32768:8:1$clwziZOoYhDcYNLi$3cfbbe8a954771bcb0369426cbd7517b593faee50d573d47bcd16e1195c843aadafe88b2afa88c2d34b363ef35a734fd631622f3ffcdb2b1c2185b3e31bb65d2'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Borrar archivos con más de 24h
now = time.time()
for f in os.listdir(UPLOAD_FOLDER):
    path = os.path.join(UPLOAD_FOLDER, f)
    if os.path.isfile(path):
        if now - os.path.getmtime(path) > 86400:
            os.remove(path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Senha incorreta')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/home')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return jsonify({ 'error': 'Não autorizado' }), 403

    file = request.files.get('images')
    if not file or not allowed_file(file.filename):
        return jsonify({ 'error': 'Arquivo inválido' }), 400

    filename = file.filename.rsplit('.', 1)[0]
    image_bytes = file.read()
    original_size = len(image_bytes)

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        output_path = os.path.join(UPLOAD_FOLDER, f"{filename}.webp")
        img.save(output_path, 'webp', quality=80, method=6)
        compressed_size = os.path.getsize(output_path)
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500

    return jsonify({
        'name': f"{filename}.webp",
        'original': round(original_size / (1024 * 1024), 2),
        'compressed': round(compressed_size / (1024 * 1024), 2)
    })

@app.route('/download/<filename>')
def download(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
