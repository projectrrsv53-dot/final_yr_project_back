# 🧠 MindSense AI – Backend

MindSense AI is an AI-powered mental health assessment system that analyzes text and speech to detect signs of depression and sentiment using deep learning models.

## 🚀 Features

- User Authentication
- Text-based Depression Detection
- Audio-based Depression Detection
- Speech-to-Text Analysis
- Multimodal Fusion Prediction
- Mood Tracking
- Patient History
- Emergency Contact Management
- MongoDB Database Integration
- REST API using FastAPI

---

## 🛠️ Tech Stack

- Python 3.11
- FastAPI
- PyTorch
- Transformers (BERT)
- Whisper
- WavLM
- MongoDB Atlas
- Motor
- Librosa
- Resemblyzer

---

## 📁 Project Structure

backend/
│
├── app.py
├── database.py
├── routes/
├── audio/
├── text/
├── fusion/
├── models/
├── uploads/
├── outputs/
├── requirements.txt

---

## ⚙️ Installation

```bash
git clone <repository-url>

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app:app --reload
```

---

## Database

MongoDB Atlas

---

## API

Runs on

```
http://127.0.0.1:8000
```

Swagger Docs

```
http://127.0.0.1:8000/docs
```

---

## Notes

Large AI models are excluded from this repository because of GitHub size limits.

---

## 👥 Authors

- Reva Gaonkar
- Riya Padwalkar
- Sanisha Faria
- Vanetta Silveira