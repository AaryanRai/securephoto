from flask import Flask, request, render_template, send_file, url_for, session
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from pymongo import MongoClient
import gridfs
import os
import io
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MongoDB Atlas connection (free tier)
MONGO_URI = 'mongodb+srv://aaryanrai:PFJ8Kt0LF0Qr7mgL@securephotocluster.zdcllpy.mongodb.net/secure_share?retryWrites=true&w=majority&appName=SecurePhotoCluster'
client = MongoClient(MONGO_URI)
db = client.secure_share
fs = gridfs.GridFS(db)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Store encryption key in MongoDB if not exists
def get_or_create_key():
    key_doc = db.encryption_keys.find_one({'id': 'main_key'})
    if not key_doc:
        key = Fernet.generate_key()
        db.encryption_keys.insert_one({'id': 'main_key', 'key': key})
        return key
    return key_doc['key']

key = get_or_create_key()
fernet = Fernet(key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# No need for uploads directory with MongoDB

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
    print("\nENCRYPTION KEY (share this securely with other parties):")
    print(key.decode())
    print("\nServer starting on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001)
