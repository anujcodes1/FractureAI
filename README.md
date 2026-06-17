# FractureAI (Bone Fracture Detection)

AI-powered bone fracture detection web application.

## Project Structure
- **`app.py`**: Flask app entrypoint (starts the server)
- **`train_model.py`**: Trains the CNN and saves the model to `models/fracture_cnn.h5`
- **`config.py`**: App configuration (SQLite DB, upload/report folders, mail settings)

## Prerequisites
- Python **3.10–3.12** (important for training because TensorFlow is used)
- pip

## 1) Setup & Install Dependencies
Open a terminal and run these commands inside the project folder:

```bat
cd c:\Users\Himanshu\Downloads\FinalYear\FractureAI
pip install --upgrade pip
pip install -r requirements.txt
```

## 2) (Optional) Train the Model
If you don’t already have the trained model at:
- `models/fracture_cnn.h5`

Run:

```bat
python train_model.py
```

This will:
- download/prepare the dataset (or generate synthetic data if download fails)
- train MobileNetV2-based binary classifier
- save: `models/fracture_cnn.h5`

## 3) Run the Web App
Start the Flask server:

```bat
python app.py
```

Then open:
- `http://127.0.0.1:5000`

### Database / Folders
On startup, the app will create (if missing):
- `instance/fractureai.db` (SQLite)
- `uploads/` (uploaded images)
- `reports/` (PDF reports)

## Email Configuration (Optional)
If the app sends emails (password reset / notifications), configure these environment variables:
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

(Defaults are defined in `config.py`, but SMTP auth usually requires your credentials.)

## Notes
- For better performance, use a GPU-enabled machine for training.
- If you only want to run the web app, you can skip training as long as `models/fracture_cnn.h5` exists.

