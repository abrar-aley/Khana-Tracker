from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "desi-tracker-secret-2024")

# ── Database config ───────────────────────────────────────────
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'khana.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── Database model ────────────────────────────────────────────
class FoodLog(db.Model):
    id         = db.Column(db.String(8),  primary_key=True)
    date       = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    meal       = db.Column(db.String(20), nullable=False)
    food_id    = db.Column(db.String(50), nullable=False)
    name       = db.Column(db.String(100),nullable=False)
    emoji      = db.Column(db.String(10), nullable=False)
    quantity   = db.Column(db.Float,      nullable=False)
    unit       = db.Column(db.String(30), nullable=False)
    calories   = db.Column(db.Integer,    nullable=False)
    protein    = db.Column(db.Float,      nullable=False)
    carbs      = db.Column(db.Float,      nullable=False)
    fat        = db.Column(db.Float,      nullable=False)

# ── Pakistani food database ───────────────────────────────────
FOOD_DB = [
    # Rice & Biryani
    {"id": "biryani_chicken", "name": "Chicken Biryani", "category": "Rice & Biryani", "calories": 190, "protein": 11, "carbs": 25, "fat": 5, "unit": "100g", "emoji": "🍚"},
    {"id": "biryani_mutton",  "name": "Mutton Biryani",  "category": "Rice & Biryani", "calories": 215, "protein": 13, "carbs": 24, "fat": 7, "unit": "100g", "emoji": "🍚"},
    {"id": "pulao_chicken",   "name": "Chicken Pulao",   "category": "Rice & Biryani", "calories": 170, "protein": 10, "carbs": 22, "fat": 4, "unit": "100g", "emoji": "🍚"},
    {"id": "zeera_rice",      "name": "Zeera Rice",      "category": "Rice & Biryani", "calories": 150, "protein": 3,  "carbs": 30, "fat": 3, "unit": "100g", "emoji": "🍚"},
    # Bread & Roti
    {"id": "roti_plain",    "name": "Plain Roti",    "category": "Bread & Roti", "calories": 71,  "protein": 2, "carbs": 14, "fat": 1,  "unit": "1 piece", "emoji": "🫓"},
    {"id": "paratha_plain", "name": "Plain Paratha", "category": "Bread & Roti", "calories": 260, "protein": 5, "carbs": 32, "fat": 13, "unit": "1 piece", "emoji": "🫓"},
    {"id": "paratha_aloo",  "name": "Aloo Paratha",  "category": "Bread & Roti", "calories": 300, "protein": 6, "carbs": 40, "fat": 13, "unit": "1 piece", "emoji": "🫓"},
    {"id": "naan_plain",    "name": "Plain Naan",    "category": "Bread & Roti", "calories": 262, "protein": 8, "carbs": 47, "fat": 5,  "unit": "1 piece", "emoji": "🫓"},
    {"id": "naan_butter",   "name": "Butter Naan",   "category": "Bread & Roti", "calories": 310, "protein": 8, "carbs": 47, "fat": 10, "unit": "1 piece", "emoji": "🫓"},
    {"id": "puri",          "name": "Puri",          "category": "Bread & Roti", "calories": 180, "protein": 3, "carbs": 22, "fat": 9,  "unit": "1 piece", "emoji": "🫓"},
    # Curries & Daal
    {"id": "daal_mash",     "name": "Daal Mash",      "category": "Curries & Daal", "calories": 105, "protein": 7,  "carbs": 15, "fat": 3,  "unit": "100g", "emoji": "🍲"},
    {"id": "daal_chana",    "name": "Daal Chana",     "category": "Curries & Daal", "calories": 120, "protein": 8,  "carbs": 18, "fat": 3,  "unit": "100g", "emoji": "🍲"},
    {"id": "daal_tarka",    "name": "Tarka Daal",     "category": "Curries & Daal", "calories": 115, "protein": 7,  "carbs": 16, "fat": 4,  "unit": "100g", "emoji": "🍲"},
    {"id": "nihari",        "name": "Nihari",         "category": "Curries & Daal", "calories": 185, "protein": 16, "carbs": 5,  "fat": 12, "unit": "100g", "emoji": "🍲"},
    {"id": "haleem",        "name": "Haleem",         "category": "Curries & Daal", "calories": 160, "protein": 14, "carbs": 14, "fat": 6,  "unit": "100g", "emoji": "🍲"},
    {"id": "chicken_karahi","name": "Chicken Karahi", "category": "Curries & Daal", "calories": 175, "protein": 18, "carbs": 4,  "fat": 10, "unit": "100g", "emoji": "🍲"},
    {"id": "mutton_karahi", "name": "Mutton Karahi",  "category": "Curries & Daal", "calories": 200, "protein": 19, "carbs": 4,  "fat": 13, "unit": "100g", "emoji": "🍲"},
    {"id": "saag",          "name": "Saag (Sarson)",  "category": "Curries & Daal", "calories": 75,  "protein": 4,  "carbs": 8,  "fat": 4,  "unit": "100g", "emoji": "🥬"},
    {"id": "aloo_gosht",    "name": "Aloo Gosht",     "category": "Curries & Daal", "calories": 145, "protein": 12, "carbs": 9,  "fat": 8,  "unit": "100g", "emoji": "🍲"},
    # BBQ & Grilled
    {"id": "seekh_kabab",    "name": "Seekh Kabab",     "category": "BBQ & Grilled", "calories": 220, "protein": 20, "carbs": 5, "fat": 14, "unit": "1 piece", "emoji": "🍢"},
    {"id": "chapli_kabab",   "name": "Chapli Kabab",    "category": "BBQ & Grilled", "calories": 290, "protein": 18, "carbs": 8, "fat": 21, "unit": "1 piece", "emoji": "🍢"},
    {"id": "chicken_tikka",  "name": "Chicken Tikka",   "category": "BBQ & Grilled", "calories": 165, "protein": 25, "carbs": 2, "fat": 6,  "unit": "100g",   "emoji": "🍗"},
    {"id": "boti_kabab",     "name": "Boti Kabab",      "category": "BBQ & Grilled", "calories": 210, "protein": 22, "carbs": 3, "fat": 13, "unit": "100g",   "emoji": "🍢"},
    {"id": "tandoori_chicken","name": "Tandoori Chicken","category": "BBQ & Grilled", "calories": 155, "protein": 23, "carbs": 3, "fat": 6,  "unit": "100g",   "emoji": "🍗"},
    # Snacks & Street Food
    {"id": "samosa",     "name": "Samosa (Aloo)",    "category": "Snacks & Street Food", "calories": 260, "protein": 4, "carbs": 28, "fat": 15, "unit": "1 piece",  "emoji": "🥟"},
    {"id": "pakora",     "name": "Pakora",           "category": "Snacks & Street Food", "calories": 80,  "protein": 2, "carbs": 8,  "fat": 5,  "unit": "1 piece",  "emoji": "🧆"},
    {"id": "gol_gappa",  "name": "Gol Gappa (6pcs)", "category": "Snacks & Street Food", "calories": 100, "protein": 2, "carbs": 18, "fat": 3,  "unit": "6 pieces", "emoji": "🫧"},
    {"id": "chaat",      "name": "Dahi Chaat",       "category": "Snacks & Street Food", "calories": 130, "protein": 4, "carbs": 22, "fat": 4,  "unit": "100g",     "emoji": "🥗"},
    {"id": "rolls",      "name": "Chicken Roll",     "category": "Snacks & Street Food", "calories": 350, "protein": 16,"carbs": 38, "fat": 14, "unit": "1 piece",  "emoji": "🌯"},
    # Desserts & Sweets
    {"id": "kheer",       "name": "Kheer",       "category": "Desserts & Sweets", "calories": 150, "protein": 4, "carbs": 26, "fat": 4,  "unit": "100g",   "emoji": "🍮"},
    {"id": "gulab_jamun", "name": "Gulab Jamun", "category": "Desserts & Sweets", "calories": 175, "protein": 2, "carbs": 30, "fat": 5,  "unit": "1 piece","emoji": "🍡"},
    {"id": "jalebi",      "name": "Jalebi",      "category": "Desserts & Sweets", "calories": 150, "protein": 1, "carbs": 32, "fat": 4,  "unit": "100g",   "emoji": "🍩"},
    {"id": "halwa_sooji", "name": "Sooji Halwa", "category": "Desserts & Sweets", "calories": 190, "protein": 3, "carbs": 30, "fat": 7,  "unit": "100g",   "emoji": "🍮"},
    {"id": "barfi",       "name": "Barfi",       "category": "Desserts & Sweets", "calories": 380, "protein": 7, "carbs": 55, "fat": 14, "unit": "100g",   "emoji": "🍬"},
    # Drinks
    {"id": "chai_doodh",    "name": "Doodh Patti Chai", "category": "Drinks", "calories": 80,  "protein": 3, "carbs": 9,  "fat": 4, "unit": "1 cup",   "emoji": "☕"},
    {"id": "lassi_sweet",   "name": "Sweet Lassi",      "category": "Drinks", "calories": 160, "protein": 5, "carbs": 26, "fat": 4, "unit": "1 glass", "emoji": "🥛"},
    {"id": "lassi_salty",   "name": "Salty Lassi",      "category": "Drinks", "calories": 100, "protein": 5, "carbs": 10, "fat": 4, "unit": "1 glass", "emoji": "🥛"},
    {"id": "rooh_afza",     "name": "Rooh Afza Drink",  "category": "Drinks", "calories": 110, "protein": 0, "carbs": 28, "fat": 0, "unit": "1 glass", "emoji": "🍹"},
    {"id": "sugarcane_juice","name": "Ganna Juice",     "category": "Drinks", "calories": 115, "protein": 0, "carbs": 27, "fat": 0, "unit": "1 glass", "emoji": "🥤"},
]

def get_today():
    return date.today().isoformat()

# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/foods")
def get_foods():
    query    = request.args.get("q", "").lower()
    category = request.args.get("category", "")
    foods = FOOD_DB
    if query:    foods = [f for f in foods if query in f["name"].lower()]
    if category: foods = [f for f in foods if f["category"] == category]
    return jsonify(foods)

@app.route("/api/categories")
def get_categories():
    return jsonify(sorted(set(f["category"] for f in FOOD_DB)))

@app.route("/api/log", methods=["GET"])
def get_log():
    day = request.args.get("date", get_today())
    entries = FoodLog.query.filter_by(date=day).all()
    data = [{
        "entry_id": e.id, "food_id": e.food_id, "name": e.name,
        "emoji": e.emoji, "meal": e.meal, "quantity": e.quantity,
        "unit": e.unit, "calories": e.calories,
        "protein": e.protein, "carbs": e.carbs, "fat": e.fat
    } for e in entries]
    totals = {
        "calories": sum(e["calories"] for e in data),
        "protein":  round(sum(e["protein"]  for e in data), 1),
        "carbs":    round(sum(e["carbs"]    for e in data), 1),
        "fat":      round(sum(e["fat"]      for e in data), 1),
    }
    return jsonify({"date": day, "entries": data, "totals": totals})

@app.route("/api/log", methods=["POST"])
def add_log():
    data    = request.get_json()
    food_id = data.get("food_id")
    qty     = float(data.get("quantity", 1))
    day     = data.get("date", get_today())
    meal    = data.get("meal", "Lunch")

    food = next((f for f in FOOD_DB if f["id"] == food_id), None)
    if not food:
        return jsonify({"error": "Food not found"}), 404

    entry = FoodLog(
        id       = str(uuid.uuid4())[:8],
        date     = day,
        meal     = meal,
        food_id  = food_id,
        name     = food["name"],
        emoji    = food["emoji"],
        quantity = qty,
        unit     = food["unit"],
        calories = round(food["calories"] * qty),
        protein  = round(food["protein"]  * qty, 1),
        carbs    = round(food["carbs"]    * qty, 1),
        fat      = round(food["fat"]      * qty, 1),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"entry_id": entry.id, "name": entry.name, "calories": entry.calories}), 201

@app.route("/api/log/<entry_id>", methods=["DELETE"])
def delete_log(entry_id):
    entry = FoodLog.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"deleted": entry_id})

@app.route("/api/weekly")
def weekly_summary():
    today = date.today()
    summary = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        entries = FoodLog.query.filter_by(date=d).all()
        summary.append({
            "date": d,
            "day": (today - timedelta(days=i)).strftime("%a"),
            "calories": sum(e.calories for e in entries)
        })
    return jsonify(summary)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates khana.db if it doesn't exist
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)