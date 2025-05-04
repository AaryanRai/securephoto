from flask import Flask, request, render_template, send_file, url_for, session, abort
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from functools import wraps
import os
import io
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Enhanced security settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/data/uploads')
app.config['ACCESS_KEY'] = os.getenv('ACCESS_KEY', secrets.token_urlsafe(32))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Generate a secure encryption key
key = Fernet.generate_key()
fernet = Fernet(key)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def require_access_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_key = request.args.get('key')
        if not access_key or not secrets.compare_digest(access_key, app.config['ACCESS_KEY']):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@require_access_key
def index():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
             if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('index.html', 
                         files=files, 
                         access_key=app.config['ACCESS_KEY'],
                         encryption_key=key.decode())

@app.route('/upload', methods=['POST'])
@require_access_key
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Read and encrypt the file
        file_content = file.read()
        encrypted_content = fernet.encrypt(file_content)
        # Save with a hash of the content as filename
        content_hash = hashlib.sha256(encrypted_content).hexdigest()[:16]
        safe_filename = f'{content_hash}_{filename}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        with open(filepath, 'wb') as f:
            f.write(encrypted_content)
        return 'File uploaded successfully', 200
    return 'File type not allowed', 400

@app.route('/download/<filename>')
@require_access_key
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            abort(404)
        # Read and decrypt the file
        with open(filepath, 'rb') as f:
            encrypted_content = f.read()
        decrypted_content = fernet.decrypt(encrypted_content)
        # Send the decrypted file
        original_filename = filename.split('_', 1)[1] if '_' in filename else filename
        return send_file(
            io.BytesIO(decrypted_content),
            download_name=original_filename,
            as_attachment=True
        )
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print('\nAccess Key (required for all operations):')
    print(app.config['ACCESS_KEY'])
    print('\nEncryption Key (share this securely with other parties):')
    print(key.decode())
    app.run(host='0.0.0.0', port=port)
@app.route('/')
def index():
    files = [file.filename for file in db.fs.files.find()]
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Read and encrypt the file content
        file_content = file.read()
        encrypted_content = fernet.encrypt(file_content)
        # Save to MongoDB GridFS
        fs.put(encrypted_content, filename=filename)
        return 'File uploaded successfully', 200
    return 'File type not allowed', 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # Get file from GridFS
        file_data = fs.find_one({'filename': filename})
        if not file_data:
            return 'File not found', 404
        
        encrypted_content = file_data.read()
        # Decrypt the content
        decrypted_content = fernet.decrypt(encrypted_content)
        # Create BytesIO object
        file_stream = io.BytesIO(decrypted_content)
        return send_file(
            file_stream,
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    # Get port from environment variable (Render uses PORT)
    port = int(os.getenv('PORT', 5001))
    
    print("\nENCRYPTION KEY (share this securely with other parties):")
    print(key.decode())
    print(f"\nServer starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
