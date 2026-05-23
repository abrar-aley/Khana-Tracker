# 🫕 Khana Tracker — Pakistani Calorie Tracker

A calorie tracking web app built around **Pakistani / desi food**, made with Flask (Python) + vanilla JS.

## Features
- 35+ Pakistani dishes with calories, protein, carbs & fat
- Log meals by type: Sehri, Breakfast, Lunch, Dinner, Snack
- Daily calorie ring with 2000 kcal goal
- 7-day weekly overview chart
- Search & filter by category
- Date navigation (track any day)

---

## Run locally

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open http://localhost:5000 in your browser.

---

## Deploy to Render (free)

1. Push this folder to a GitHub repo
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — just click **Deploy**
5. Your app will be live at `https://khana-tracker.onrender.com` (or similar)

---

## Project structure

```
desi-calorie-tracker/
├── app.py               ← Flask backend + food database + API routes
├── requirements.txt     ← Python dependencies
├── render.yaml          ← Render deploy config
├── Procfile             ← gunicorn start command
├── templates/
│   └── index.html       ← Main HTML page
└── static/
    ├── css/style.css    ← Styling
    └── js/app.js        ← Frontend logic
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/foods?q=biryani` | Search foods |
| GET | `/api/categories` | All categories |
| GET | `/api/log?date=2024-01-15` | Get day's log |
| POST | `/api/log` | Add food entry |
| DELETE | `/api/log/<entry_id>` | Remove entry |
| GET | `/api/weekly` | 7-day summary |

> **Note:** Food log is stored in memory (resets on server restart). For a persistent app, swap the `food_log` dict in `app.py` with SQLite using Flask-SQLAlchemy.
