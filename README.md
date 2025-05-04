# Secure Photo Share

A secure photo-sharing web application that allows parties to exchange encrypted files through a cloud platform.

## Features

- Upload photos and PDFs (PNG, JPG, JPEG, PDF supported)
- Automatic file encryption using Fernet symmetric encryption
- Cloud storage using MongoDB Atlas (free tier)
- On-the-fly decryption when downloading files
- Simple and clean web interface
- Accessible from anywhere
- Persistent encryption key storage

## Requirements

- Python 3.x
- Flask
- cryptography
- MongoDB Atlas account (free tier)
- Render.com account (free tier)

## Setup Instructions

1. Create a free MongoDB Atlas account:
   - Go to https://www.mongodb.com/cloud/atlas/register
   - Create a new cluster (free tier)
   - Create a database user and get your connection string
   - Replace the `MONGO_URI` in `app.py` with your connection string

2. Deploy to Render (free tier):
   - Go to https://render.com
   - Create a new Web Service
   - Connect your GitHub repository
   - Set the following:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`

3. After deployment:
   - The encryption key will be automatically generated and stored in MongoDB
   - Share the application URL with others who need to share files
   - The encryption key can be retrieved from the MongoDB database

4. Access the web interface:
   - The application will be available at your Render URL
   - Files are encrypted in the cloud and can be accessed from anywhere

## Security Notes

- The encryption key is stored securely in MongoDB and persists between restarts
- All files are encrypted before storage and decrypted on-the-fly when downloaded
- Maximum file size is limited to 16MB
- Files are stored encrypted in MongoDB Atlas
- Use HTTPS (provided by Render) for secure file transfer
- Share the encryption key through secure channels only
