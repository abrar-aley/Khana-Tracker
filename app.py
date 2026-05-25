from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "desi-tracker-secret-2024")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'khana.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── Models ────────────────────────────────────────────────────
class FoodLog(db.Model):
    id       = db.Column(db.String(8),   primary_key=True)
    date     = db.Column(db.String(10),  nullable=False)
    meal     = db.Column(db.String(20),  nullable=False)
    food_id  = db.Column(db.String(50),  nullable=False)
    name     = db.Column(db.String(100), nullable=False)
    emoji    = db.Column(db.String(10),  nullable=False)
    quantity = db.Column(db.Float,       nullable=False)
    unit     = db.Column(db.String(30),  nullable=False)
    calories = db.Column(db.Integer,     nullable=False)
    protein  = db.Column(db.Float,       nullable=False)
    carbs    = db.Column(db.Float,       nullable=False)
    fat      = db.Column(db.Float,       nullable=False)

class CustomFood(db.Model):
    id       = db.Column(db.String(50),  primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50),  nullable=False)
    calories = db.Column(db.Integer,     nullable=False)
    protein  = db.Column(db.Float,       nullable=False)
    carbs    = db.Column(db.Float,       nullable=False)
    fat      = db.Column(db.Float,       nullable=False)
    unit     = db.Column(db.String(30),  nullable=False)
    emoji    = db.Column(db.String(10),  nullable=False)

# ── Built-in food database ────────────────────────────────────
FOOD_DB = [
    {"id": "biryani_chicken",  "name": "Chicken Biryani",  "category": "Rice & Biryani",       "calories": 190, "protein": 11, "carbs": 25, "fat": 5,  "unit": "100g",    "emoji": "🍚"},
    {"id": "biryani_mutton",   "name": "Mutton Biryani",   "category": "Rice & Biryani",       "calories": 215, "protein": 13, "carbs": 24, "fat": 7,  "unit": "100g",    "emoji": "🍚"},
    {"id": "pulao_chicken",    "name": "Chicken Pulao",    "category": "Rice & Biryani",       "calories": 170, "protein": 10, "carbs": 22, "fat": 4,  "unit": "100g",    "emoji": "🍚"},
    {"id": "zeera_rice",       "name": "Zeera Rice",       "category": "Rice & Biryani",       "calories": 150, "protein": 3,  "carbs": 30, "fat": 3,  "unit": "100g",    "emoji": "🍚"},
    {"id": "roti_plain",       "name": "Plain Roti",       "category": "Bread & Roti",         "calories": 71,  "protein": 2,  "carbs": 14, "fat": 1,  "unit": "1 piece", "emoji": "🫓"},
    {"id": "paratha_plain",    "name": "Plain Paratha",    "category": "Bread & Roti",         "calories": 260, "protein": 5,  "carbs": 32, "fat": 13, "unit": "1 piece", "emoji": "🫓"},
    {"id": "paratha_aloo",     "name": "Aloo Paratha",     "category": "Bread & Roti",         "calories": 300, "protein": 6,  "carbs": 40, "fat": 13, "unit": "1 piece", "emoji": "🫓"},
    {"id": "naan_plain",       "name": "Plain Naan",       "category": "Bread & Roti",         "calories": 262, "protein": 8,  "carbs": 47, "fat": 5,  "unit": "1 piece", "emoji": "🫓"},
    {"id": "naan_butter",      "name": "Butter Naan",      "category": "Bread & Roti",         "calories": 310, "protein": 8,  "carbs": 47, "fat": 10, "unit": "1 piece", "emoji": "🫓"},
    {"id": "puri",             "name": "Puri",             "category": "Bread & Roti",         "calories": 180, "protein": 3,  "carbs": 22, "fat": 9,  "unit": "1 piece", "emoji": "🫓"},
    {"id": "daal_mash",        "name": "Daal Mash",        "category": "Curries & Daal",       "calories": 105, "protein": 7,  "carbs": 15, "fat": 3,  "unit": "100g",    "emoji": "🍲"},
    {"id": "daal_chana",       "name": "Daal Chana",       "category": "Curries & Daal",       "calories": 120, "protein": 8,  "carbs": 18, "fat": 3,  "unit": "100g",    "emoji": "🍲"},
    {"id": "daal_tarka",       "name": "Tarka Daal",       "category": "Curries & Daal",       "calories": 115, "protein": 7,  "carbs": 16, "fat": 4,  "unit": "100g",    "emoji": "🍲"},
    {"id": "nihari",           "name": "Nihari",           "category": "Curries & Daal",       "calories": 185, "protein": 16, "carbs": 5,  "fat": 12, "unit": "100g",    "emoji": "🍲"},
    {"id": "haleem",           "name": "Haleem",           "category": "Curries & Daal",       "calories": 160, "protein": 14, "carbs": 14, "fat": 6,  "unit": "100g",    "emoji": "🍲"},
    {"id": "chicken_karahi",   "name": "Chicken Karahi",   "category": "Curries & Daal",       "calories": 175, "protein": 18, "carbs": 4,  "fat": 10, "unit": "100g",    "emoji": "🍲"},
    {"id": "mutton_karahi",    "name": "Mutton Karahi",    "category": "Curries & Daal",       "calories": 200, "protein": 19, "carbs": 4,  "fat": 13, "unit": "100g",    "emoji": "🍲"},
    {"id": "saag",             "name": "Saag (Sarson)",    "category": "Curries & Daal",       "calories": 75,  "protein": 4,  "carbs": 8,  "fat": 4,  "unit": "100g",    "emoji": "🥬"},
    {"id": "aloo_gosht",       "name": "Aloo Gosht",       "category": "Curries & Daal",       "calories": 145, "protein": 12, "carbs": 9,  "fat": 8,  "unit": "100g",    "emoji": "🍲"},
    {"id": "seekh_kabab",      "name": "Seekh Kabab",      "category": "BBQ & Grilled",        "calories": 220, "protein": 20, "carbs": 5,  "fat": 14, "unit": "1 piece", "emoji": "🍢"},
    {"id": "chapli_kabab",     "name": "Chapli Kabab",     "category": "BBQ & Grilled",        "calories": 290, "protein": 18, "carbs": 8,  "fat": 21, "unit": "1 piece", "emoji": "🍢"},
    {"id": "chicken_tikka",    "name": "Chicken Tikka",    "category": "BBQ & Grilled",        "calories": 165, "protein": 25, "carbs": 2,  "fat": 6,  "unit": "100g",    "emoji": "🍗"},
    {"id": "boti_kabab",       "name": "Boti Kabab",       "category": "BBQ & Grilled",        "calories": 210, "protein": 22, "carbs": 3,  "fat": 13, "unit": "100g",    "emoji": "🍢"},
    {"id": "tandoori_chicken", "name": "Tandoori Chicken", "category": "BBQ & Grilled",        "calories": 155, "protein": 23, "carbs": 3,  "fat": 6,  "unit": "100g",    "emoji": "🍗"},
    {"id": "samosa",           "name": "Samosa (Aloo)",    "category": "Snacks & Street Food", "calories": 260, "protein": 4,  "carbs": 28, "fat": 15, "unit": "1 piece", "emoji": "🥟"},
    {"id": "pakora",           "name": "Pakora",           "category": "Snacks & Street Food", "calories": 80,  "protein": 2,  "carbs": 8,  "fat": 5,  "unit": "1 piece", "emoji": "🧆"},
    {"id": "gol_gappa",        "name": "Gol Gappa (6pcs)", "category": "Snacks & Street Food", "calories": 100, "protein": 2,  "carbs": 18, "fat": 3,  "unit": "6 pieces","emoji": "🫧"},
    {"id": "chaat",            "name": "Dahi Chaat",       "category": "Snacks & Street Food", "calories": 130, "protein": 4,  "carbs": 22, "fat": 4,  "unit": "100g",    "emoji": "🥗"},
    {"id": "rolls",            "name": "Chicken Roll",     "category": "Snacks & Street Food", "calories": 350, "protein": 16, "carbs": 38, "fat": 14, "unit": "1 piece", "emoji": "🌯"},
    {"id": "kheer",            "name": "Kheer",            "category": "Desserts & Sweets",    "calories": 150, "protein": 4,  "carbs": 26, "fat": 4,  "unit": "100g",    "emoji": "🍮"},
    {"id": "gulab_jamun",      "name": "Gulab Jamun",      "category": "Desserts & Sweets",    "calories": 175, "protein": 2,  "carbs": 30, "fat": 5,  "unit": "1 piece", "emoji": "🍡"},
    {"id": "jalebi",           "name": "Jalebi",           "category": "Desserts & Sweets",    "calories": 150, "protein": 1,  "carbs": 32, "fat": 4,  "unit": "100g",    "emoji": "🍩"},
    {"id": "halwa_sooji",      "name": "Sooji Halwa",      "category": "Desserts & Sweets",    "calories": 190, "protein": 3,  "carbs": 30, "fat": 7,  "unit": "100g",    "emoji": "🍮"},
    {"id": "barfi",            "name": "Barfi",            "category": "Desserts & Sweets",    "calories": 380, "protein": 7,  "carbs": 55, "fat": 14, "unit": "100g",    "emoji": "🍬"},
    {"id": "chai_doodh",       "name": "Doodh Patti Chai", "category": "Drinks",              "calories": 80,  "protein": 3,  "carbs": 9,  "fat": 4,  "unit": "1 cup",   "emoji": "☕"},
    {"id": "lassi_sweet",      "name": "Sweet Lassi",      "category": "Drinks",              "calories": 160, "protein": 5,  "carbs": 26, "fat": 4,  "unit": "1 glass", "emoji": "🥛"},
    {"id": "lassi_salty",      "name": "Salty Lassi",      "category": "Drinks",              "calories": 100, "protein": 5,  "carbs": 10, "fat": 4,  "unit": "1 glass", "emoji": "🥛"},
    {"id": "rooh_afza",        "name": "Rooh Afza Drink",  "category": "Drinks",              "calories": 110, "protein": 0,  "carbs": 28, "fat": 0,  "unit": "1 glass", "emoji": "🍹"},
    {"id": "sugarcane_juice",  "name": "Ganna Juice",      "category": "Drinks",              "calories": 115, "protein": 0,  "carbs": 27, "fat": 0,  "unit": "1 glass", "emoji": "🥤"},

    # ── New foods added ───────────────────────────────────────
    # Desi Home Food
    {"id": "beef_karahi", "name": "Beef Karahi", "category": "Desi Home Food", "calories": 200, "protein": 20, "carbs": 4, "fat": 13, "unit": "100g", "emoji": "🍲"},
    {"id": "beef_qorma", "name": "Beef Qorma", "category": "Desi Home Food", "calories": 210, "protein": 18, "carbs": 8, "fat": 13, "unit": "100g", "emoji": "🍲"},
    {"id": "mutton_qorma", "name": "Mutton Qorma", "category": "Desi Home Food", "calories": 220, "protein": 19, "carbs": 8, "fat": 14, "unit": "100g", "emoji": "🍲"},
    {"id": "chicken_qorma", "name": "Chicken Qorma", "category": "Desi Home Food", "calories": 190, "protein": 17, "carbs": 8, "fat": 11, "unit": "100g", "emoji": "🍲"},
    {"id": "paya", "name": "Paya", "category": "Desi Home Food", "calories": 150, "protein": 14, "carbs": 4, "fat": 9, "unit": "100g", "emoji": "🍲"},
    {"id": "daal_chawal", "name": "Daal Chawal", "category": "Desi Home Food", "calories": 160, "protein": 7, "carbs": 28, "fat": 3, "unit": "100g", "emoji": "🍚"},
    {"id": "daal_moong", "name": "Daal Moong", "category": "Desi Home Food", "calories": 100, "protein": 7, "carbs": 16, "fat": 1, "unit": "100g", "emoji": "🍲"},
    {"id": "chana_curry", "name": "Chana Curry", "category": "Desi Home Food", "calories": 130, "protein": 7, "carbs": 20, "fat": 3, "unit": "100g", "emoji": "🍲"},
    {"id": "rajma", "name": "Rajma", "category": "Desi Home Food", "calories": 125, "protein": 8, "carbs": 20, "fat": 2, "unit": "100g", "emoji": "🍲"},
    {"id": "bhindi_masala", "name": "Bhindi Masala", "category": "Desi Home Food", "calories": 80, "protein": 2, "carbs": 10, "fat": 4, "unit": "100g", "emoji": "🥬"},
    {"id": "palak_paneer", "name": "Palak Paneer", "category": "Desi Home Food", "calories": 150, "protein": 7, "carbs": 8, "fat": 11, "unit": "100g", "emoji": "🥬"},
    {"id": "baingan_bharta", "name": "Baingan Bharta", "category": "Desi Home Food", "calories": 90, "protein": 2, "carbs": 10, "fat": 5, "unit": "100g", "emoji": "🥬"},
    {"id": "keema", "name": "Keema", "category": "Desi Home Food", "calories": 200, "protein": 18, "carbs": 4, "fat": 13, "unit": "100g", "emoji": "🍲"},
    {"id": "chicken_curry", "name": "Chicken Curry", "category": "Desi Home Food", "calories": 165, "protein": 17, "carbs": 5, "fat": 9, "unit": "100g", "emoji": "🍲"},
    {"id": "anda_curry", "name": "Anda Curry", "category": "Desi Home Food", "calories": 140, "protein": 10, "carbs": 4, "fat": 10, "unit": "100g", "emoji": "🍳"},
    {"id": "omelette", "name": "Omelette", "category": "Desi Home Food", "calories": 150, "protein": 10, "carbs": 1, "fat": 12, "unit": "1 piece", "emoji": "🍳"},
    {"id": "boiled_egg", "name": "Boiled Egg", "category": "Desi Home Food", "calories": 78, "protein": 6, "carbs": 1, "fat": 5, "unit": "1 piece", "emoji": "🥚"},
    {"id": "fried_egg", "name": "Fried Egg", "category": "Desi Home Food", "calories": 90, "protein": 6, "carbs": 0, "fat": 7, "unit": "1 piece", "emoji": "🍳"},
    {"id": "chapati", "name": "Chapati", "category": "Desi Home Food", "calories": 71, "protein": 2, "carbs": 14, "fat": 1, "unit": "1 piece", "emoji": "🫓"},
    {"id": "mooli_paratha", "name": "Mooli Paratha", "category": "Desi Home Food", "calories": 280, "protein": 5, "carbs": 35, "fat": 13, "unit": "1 piece", "emoji": "🫓"},
    {"id": "kulcha", "name": "Kulcha", "category": "Desi Home Food", "calories": 240, "protein": 7, "carbs": 44, "fat": 4, "unit": "1 piece", "emoji": "🫓"},
    {"id": "tandoori_roti", "name": "Tandoori Roti", "category": "Desi Home Food", "calories": 100, "protein": 4, "carbs": 18, "fat": 1, "unit": "1 piece", "emoji": "🫓"},
    {"id": "plain_rice", "name": "Plain Rice", "category": "Desi Home Food", "calories": 130, "protein": 3, "carbs": 28, "fat": 0, "unit": "100g", "emoji": "🍚"},
    {"id": "beef_pulao", "name": "Beef Pulao", "category": "Desi Home Food", "calories": 175, "protein": 12, "carbs": 22, "fat": 5, "unit": "100g", "emoji": "🍚"},
    {"id": "beef_biryani", "name": "Beef Biryani", "category": "Desi Home Food", "calories": 210, "protein": 14, "carbs": 24, "fat": 7, "unit": "100g", "emoji": "🍚"},
    {"id": "sindhi_biryani", "name": "Sindhi Biryani", "category": "Desi Home Food", "calories": 200, "protein": 12, "carbs": 25, "fat": 6, "unit": "100g", "emoji": "🍚"},
    {"id": "memoni_biryani", "name": "Memoni Biryani", "category": "Desi Home Food", "calories": 205, "protein": 13, "carbs": 24, "fat": 7, "unit": "100g", "emoji": "🍚"},
    {"id": "hyderabadi_biryani", "name": "Hyderabadi Biryani", "category": "Desi Home Food", "calories": 195, "protein": 12, "carbs": 24, "fat": 6, "unit": "100g", "emoji": "🍚"},
    {"id": "chicken_yakhni_pulao", "name": "Chicken Yakhni Pulao", "category": "Desi Home Food", "calories": 170, "protein": 11, "carbs": 22, "fat": 4, "unit": "100g", "emoji": "🍚"},
    {"id": "shami_kebab", "name": "Shami Kebab", "category": "Desi Home Food", "calories": 180, "protein": 14, "carbs": 10, "fat": 9, "unit": "1 piece", "emoji": "🍢"},
    {"id": "malai_boti", "name": "Malai Boti", "category": "Desi Home Food", "calories": 220, "protein": 22, "carbs": 2, "fat": 14, "unit": "100g", "emoji": "🍗"},
    {"id": "bihari_boti", "name": "Bihari Boti", "category": "Desi Home Food", "calories": 215, "protein": 21, "carbs": 3, "fat": 13, "unit": "100g", "emoji": "🍢"},
    {"id": "tikka_boti", "name": "Tikka Boti", "category": "Desi Home Food", "calories": 160, "protein": 22, "carbs": 2, "fat": 7, "unit": "100g", "emoji": "🍢"},
    {"id": "reshmi_kebab", "name": "Reshmi Kebab", "category": "Desi Home Food", "calories": 230, "protein": 20, "carbs": 4, "fat": 15, "unit": "100g", "emoji": "🍢"},
    {"id": "chicken_handi", "name": "Chicken Handi", "category": "Desi Home Food", "calories": 185, "protein": 18, "carbs": 5, "fat": 11, "unit": "100g", "emoji": "🍲"},
    {"id": "black_pepper_chicken", "name": "Black Pepper Chicken", "category": "Desi Home Food", "calories": 175, "protein": 19, "carbs": 4, "fat": 10, "unit": "100g", "emoji": "🍗"},
    {"id": "butter_chicken", "name": "Butter Chicken", "category": "Desi Home Food", "calories": 190, "protein": 18, "carbs": 8, "fat": 11, "unit": "100g", "emoji": "🍗"},
    {"id": "chicken_jalfrezi", "name": "Chicken Jalfrezi", "category": "Desi Home Food", "calories": 160, "protein": 18, "carbs": 6, "fat": 8, "unit": "100g", "emoji": "🍲"},
    {"id": "matar_paneer", "name": "Matar Paneer", "category": "Desi Home Food", "calories": 145, "protein": 7, "carbs": 12, "fat": 8, "unit": "100g", "emoji": "🥬"},
    {"id": "aloo_matar", "name": "Aloo Matar", "category": "Desi Home Food", "calories": 110, "protein": 4, "carbs": 18, "fat": 3, "unit": "100g", "emoji": "🥬"},
    {"id": "aloo_palak", "name": "Aloo Palak", "category": "Desi Home Food", "calories": 100, "protein": 3, "carbs": 16, "fat": 3, "unit": "100g", "emoji": "🥬"},
    {"id": "aloo_bhujia", "name": "Aloo Bhujia", "category": "Desi Home Food", "calories": 95, "protein": 2, "carbs": 14, "fat": 4, "unit": "100g", "emoji": "🥬"},
    {"id": "lauki_curry", "name": "Lauki Curry", "category": "Desi Home Food", "calories": 60, "protein": 2, "carbs": 8, "fat": 2, "unit": "100g", "emoji": "🥬"},
    {"id": "tinda_masala", "name": "Tinda Masala", "category": "Desi Home Food", "calories": 70, "protein": 2, "carbs": 9, "fat": 3, "unit": "100g", "emoji": "🥬"},
    {"id": "karela_fry", "name": "Karela Fry", "category": "Desi Home Food", "calories": 75, "protein": 2, "carbs": 8, "fat": 4, "unit": "100g", "emoji": "🥬"},
    {"id": "mix_vegetable", "name": "Mix Vegetable", "category": "Desi Home Food", "calories": 85, "protein": 3, "carbs": 11, "fat": 3, "unit": "100g", "emoji": "🥬"},
    {"id": "cabbage_curry", "name": "Cabbage Curry", "category": "Desi Home Food", "calories": 70, "protein": 2, "carbs": 9, "fat": 3, "unit": "100g", "emoji": "🥬"},
    {"id": "chicken_kofta", "name": "Chicken Kofta", "category": "Desi Home Food", "calories": 170, "protein": 16, "carbs": 6, "fat": 9, "unit": "100g", "emoji": "🍲"},
    {"id": "beef_kofta", "name": "Beef Kofta", "category": "Desi Home Food", "calories": 185, "protein": 16, "carbs": 6, "fat": 11, "unit": "100g", "emoji": "🍲"},
    {"id": "mutton_kofta", "name": "Mutton Kofta", "category": "Desi Home Food", "calories": 190, "protein": 17, "carbs": 6, "fat": 12, "unit": "100g", "emoji": "🍲"},
    # Street Food
    {"id": "dahi_bhallay", "name": "Dahi Bhallay", "category": "Street Food", "calories": 180, "protein": 7, "carbs": 25, "fat": 6, "unit": "100g", "emoji": "🥗"},
    {"id": "papri_chaat", "name": "Papri Chaat", "category": "Street Food", "calories": 200, "protein": 5, "carbs": 30, "fat": 7, "unit": "100g", "emoji": "🥗"},
    {"id": "vegetable_samosa", "name": "Vegetable Samosa", "category": "Street Food", "calories": 220, "protein": 4, "carbs": 26, "fat": 12, "unit": "1 piece", "emoji": "🥟"},
    {"id": "chicken_samosa", "name": "Chicken Samosa", "category": "Street Food", "calories": 250, "protein": 12, "carbs": 24, "fat": 12, "unit": "1 piece", "emoji": "🥟"},
    {"id": "beef_samosa", "name": "Beef Samosa", "category": "Street Food", "calories": 260, "protein": 13, "carbs": 24, "fat": 14, "unit": "1 piece", "emoji": "🥟"},
    {"id": "paratha_roll", "name": "Paratha Roll", "category": "Street Food", "calories": 380, "protein": 15, "carbs": 42, "fat": 17, "unit": "1 piece", "emoji": "🌯"},
    {"id": "shawarma", "name": "Shawarma", "category": "Street Food", "calories": 350, "protein": 18, "carbs": 35, "fat": 14, "unit": "1 piece", "emoji": "🌯"},
    {"id": "chicken_shawarma", "name": "Chicken Shawarma", "category": "Street Food", "calories": 340, "protein": 20, "carbs": 33, "fat": 13, "unit": "1 piece", "emoji": "🌯"},
    {"id": "beef_shawarma", "name": "Beef Shawarma", "category": "Street Food", "calories": 370, "protein": 19, "carbs": 34, "fat": 15, "unit": "1 piece", "emoji": "🌯"},
    {"id": "bun_kebab", "name": "Bun Kebab", "category": "Street Food", "calories": 300, "protein": 14, "carbs": 32, "fat": 13, "unit": "1 piece", "emoji": "🍔"},
    {"id": "anda_shami_burger", "name": "Anda Shami Burger", "category": "Street Food", "calories": 350, "protein": 16, "carbs": 34, "fat": 16, "unit": "1 piece", "emoji": "🍔"},
    {"id": "chana_chaat", "name": "Chana Chaat", "category": "Street Food", "calories": 140, "protein": 6, "carbs": 22, "fat": 3, "unit": "100g", "emoji": "🥗"},
    {"id": "fruit_chaat", "name": "Fruit Chaat", "category": "Street Food", "calories": 80, "protein": 1, "carbs": 18, "fat": 0, "unit": "100g", "emoji": "🍎"},
    {"id": "kulfi", "name": "Kulfi", "category": "Street Food", "calories": 170, "protein": 4, "carbs": 24, "fat": 7, "unit": "1 piece", "emoji": "🍦"},
    {"id": "falooda", "name": "Falooda", "category": "Street Food", "calories": 220, "protein": 5, "carbs": 38, "fat": 6, "unit": "1 glass", "emoji": "🍹"},
    {"id": "rabri", "name": "Rabri", "category": "Street Food", "calories": 180, "protein": 5, "carbs": 26, "fat": 7, "unit": "100g", "emoji": "🍮"},
    {"id": "gola_ganda", "name": "Gola Ganda", "category": "Street Food", "calories": 60, "protein": 0, "carbs": 15, "fat": 0, "unit": "1 piece", "emoji": "🧊"},
    {"id": "tawa_piece", "name": "Tawa Piece", "category": "Street Food", "calories": 250, "protein": 20, "carbs": 4, "fat": 18, "unit": "100g", "emoji": "🍗"},
    {"id": "katakat", "name": "Katakat", "category": "Street Food", "calories": 220, "protein": 18, "carbs": 5, "fat": 15, "unit": "100g", "emoji": "🍲"},
    {"id": "sajji", "name": "Sajji", "category": "Street Food", "calories": 190, "protein": 22, "carbs": 2, "fat": 11, "unit": "100g", "emoji": "🍗"},
    {"id": "fish_fry", "name": "Fish Fry", "category": "Street Food", "calories": 200, "protein": 18, "carbs": 8, "fat": 11, "unit": "100g", "emoji": "🐟"},
    {"id": "chicken_corn_soup", "name": "Chicken Corn Soup", "category": "Street Food", "calories": 120, "protein": 8, "carbs": 15, "fat": 3, "unit": "1 bowl", "emoji": "🍜"},
    {"id": "aloo_tikki", "name": "Aloo Tikki", "category": "Street Food", "calories": 150, "protein": 3, "carbs": 22, "fat": 6, "unit": "1 piece", "emoji": "🥔"},
    {"id": "chicken_cheese_roll", "name": "Chicken Cheese Roll", "category": "Street Food", "calories": 420, "protein": 20, "carbs": 40, "fat": 20, "unit": "1 piece", "emoji": "🌯"},
    {"id": "zinger_roll", "name": "Zinger Roll", "category": "Street Food", "calories": 450, "protein": 22, "carbs": 42, "fat": 22, "unit": "1 piece", "emoji": "🌯"},
    {"id": "anday_wala_burger", "name": "Anday Wala Burger", "category": "Street Food", "calories": 380, "protein": 18, "carbs": 35, "fat": 18, "unit": "1 piece", "emoji": "🍔"},
    {"id": "anda_paratha_roll", "name": "Anda Paratha Roll", "category": "Street Food", "calories": 400, "protein": 16, "carbs": 42, "fat": 18, "unit": "1 piece", "emoji": "🌯"},
    {"id": "chicken_mayo_roll", "name": "Chicken Mayo Roll", "category": "Street Food", "calories": 390, "protein": 18, "carbs": 38, "fat": 18, "unit": "1 piece", "emoji": "🌯"},
    {"id": "spicy_shawarma", "name": "Spicy Shawarma", "category": "Street Food", "calories": 360, "protein": 20, "carbs": 34, "fat": 15, "unit": "1 piece", "emoji": "🌯"},
    {"id": "chicken_cheese_fries", "name": "Chicken Cheese Fries", "category": "Street Food", "calories": 480, "protein": 18, "carbs": 45, "fat": 25, "unit": "1 serving", "emoji": "🍟"},
    {"id": "loaded_fries", "name": "Loaded Fries", "category": "Street Food", "calories": 450, "protein": 10, "carbs": 50, "fat": 24, "unit": "1 serving", "emoji": "🍟"},
    {"id": "masala_fries", "name": "Masala Fries", "category": "Street Food", "calories": 350, "protein": 5, "carbs": 48, "fat": 16, "unit": "1 serving", "emoji": "🍟"},
    {"id": "spicy_chips", "name": "Spicy Chips", "category": "Street Food", "calories": 300, "protein": 4, "carbs": 38, "fat": 15, "unit": "1 serving", "emoji": "🍟"},
    {"id": "dynamite_fries", "name": "Dynamite Fries", "category": "Street Food", "calories": 420, "protein": 8, "carbs": 46, "fat": 22, "unit": "1 serving", "emoji": "🍟"},
    # Chinese Food
    {"id": "chicken_manchurian", "name": "Chicken Manchurian", "category": "Chinese Food", "calories": 220, "protein": 18, "carbs": 15, "fat": 9, "unit": "100g", "emoji": "🍛"},
    {"id": "chicken_chow_mein", "name": "Chicken Chow Mein", "category": "Chinese Food", "calories": 180, "protein": 12, "carbs": 22, "fat": 5, "unit": "100g", "emoji": "🍜"},
    {"id": "egg_fried_rice", "name": "Egg Fried Rice", "category": "Chinese Food", "calories": 170, "protein": 5, "carbs": 28, "fat": 5, "unit": "100g", "emoji": "🍚"},
    {"id": "chicken_fried_rice", "name": "Chicken Fried Rice", "category": "Chinese Food", "calories": 185, "protein": 10, "carbs": 26, "fat": 5, "unit": "100g", "emoji": "🍚"},
    {"id": "vegetable_fried_rice", "name": "Vegetable Fried Rice", "category": "Chinese Food", "calories": 150, "protein": 4, "carbs": 28, "fat": 3, "unit": "100g", "emoji": "🍚"},
    {"id": "hot_sour_soup", "name": "Hot and Sour Soup", "category": "Chinese Food", "calories": 80, "protein": 5, "carbs": 10, "fat": 2, "unit": "1 bowl", "emoji": "🍜"},
    {"id": "chicken_shashlik", "name": "Chicken Shashlik", "category": "Chinese Food", "calories": 175, "protein": 18, "carbs": 8, "fat": 8, "unit": "100g", "emoji": "🍢"},
    {"id": "chicken_chili_dry", "name": "Chicken Chili Dry", "category": "Chinese Food", "calories": 200, "protein": 18, "carbs": 10, "fat": 10, "unit": "100g", "emoji": "🌶️"},
    {"id": "kung_pao_chicken", "name": "Kung Pao Chicken", "category": "Chinese Food", "calories": 190, "protein": 16, "carbs": 12, "fat": 9, "unit": "100g", "emoji": "🍛"},
    {"id": "spring_rolls", "name": "Spring Rolls", "category": "Chinese Food", "calories": 120, "protein": 4, "carbs": 16, "fat": 5, "unit": "1 piece", "emoji": "🥟"},
    {"id": "dynamite_chicken", "name": "Dynamite Chicken", "category": "Chinese Food", "calories": 280, "protein": 18, "carbs": 18, "fat": 16, "unit": "100g", "emoji": "🔥"},
    {"id": "chinese_platter", "name": "Chinese Platter", "category": "Chinese Food", "calories": 350, "protein": 20, "carbs": 35, "fat": 14, "unit": "1 serving", "emoji": "🍽️"},
    {"id": "sweet_sour_chicken", "name": "Sweet and Sour Chicken", "category": "Chinese Food", "calories": 200, "protein": 14, "carbs": 22, "fat": 6, "unit": "100g", "emoji": "🍗"},
    {"id": "chicken_tempura", "name": "Chicken Tempura", "category": "Chinese Food", "calories": 240, "protein": 16, "carbs": 20, "fat": 10, "unit": "100g", "emoji": "🍤"},
    {"id": "szechuan_chicken", "name": "Szechuan Chicken", "category": "Chinese Food", "calories": 210, "protein": 17, "carbs": 12, "fat": 11, "unit": "100g", "emoji": "🌶️"},
    {"id": "thai_soup", "name": "Thai Soup", "category": "Chinese Food", "calories": 90, "protein": 5, "carbs": 12, "fat": 2, "unit": "1 bowl", "emoji": "🍜"},
    {"id": "dragon_chicken", "name": "Dragon Chicken", "category": "Chinese Food", "calories": 260, "protein": 19, "carbs": 14, "fat": 15, "unit": "100g", "emoji": "🔥"},
    {"id": "chicken_cashew_nuts", "name": "Chicken Cashew Nuts", "category": "Chinese Food", "calories": 230, "protein": 18, "carbs": 12, "fat": 13, "unit": "100g", "emoji": "🍗"},
    {"id": "chicken_black_pepper", "name": "Chicken Black Pepper", "category": "Chinese Food", "calories": 195, "protein": 18, "carbs": 8, "fat": 11, "unit": "100g", "emoji": "🍗"},
    {"id": "vegetable_chow_mein", "name": "Vegetable Chow Mein", "category": "Chinese Food", "calories": 150, "protein": 4, "carbs": 25, "fat": 4, "unit": "100g", "emoji": "🍜"},
    {"id": "chicken_chow_fun", "name": "Chicken Chow Fun", "category": "Chinese Food", "calories": 170, "protein": 11, "carbs": 22, "fat": 4, "unit": "100g", "emoji": "🍜"},
    {"id": "spicy_noodles", "name": "Spicy Noodles", "category": "Chinese Food", "calories": 200, "protein": 8, "carbs": 30, "fat": 6, "unit": "100g", "emoji": "🍜"},
    {"id": "singaporean_rice", "name": "Singaporean Rice", "category": "Chinese Food", "calories": 220, "protein": 12, "carbs": 28, "fat": 7, "unit": "100g", "emoji": "🍚"},
    {"id": "chicken_drumsticks", "name": "Chicken Drumsticks", "category": "Chinese Food", "calories": 190, "protein": 18, "carbs": 6, "fat": 11, "unit": "100g", "emoji": "🍗"},
    {"id": "crispy_beef", "name": "Crispy Beef", "category": "Chinese Food", "calories": 280, "protein": 18, "carbs": 20, "fat": 15, "unit": "100g", "emoji": "🥩"},
    {"id": "honey_chicken", "name": "Honey Chicken", "category": "Chinese Food", "calories": 210, "protein": 15, "carbs": 20, "fat": 8, "unit": "100g", "emoji": "🍯"},
    {"id": "chicken_garlic_sauce", "name": "Chicken with Garlic Sauce", "category": "Chinese Food", "calories": 185, "protein": 17, "carbs": 8, "fat": 10, "unit": "100g", "emoji": "🍗"},
    {"id": "chicken_oyster_sauce", "name": "Chicken Oyster Sauce", "category": "Chinese Food", "calories": 180, "protein": 17, "carbs": 7, "fat": 9, "unit": "100g", "emoji": "🍗"},
    {"id": "chicken_hot_garlic", "name": "Chicken Hot Garlic", "category": "Chinese Food", "calories": 195, "protein": 17, "carbs": 10, "fat": 10, "unit": "100g", "emoji": "🌶️"},
    {"id": "chicken_egg_foo_young", "name": "Chicken Egg Foo Young", "category": "Chinese Food", "calories": 160, "protein": 12, "carbs": 8, "fat": 9, "unit": "100g", "emoji": "🍳"},
    # Fast Food
    {"id": "zinger_burger", "name": "Zinger Burger", "category": "Fast Food", "calories": 520, "protein": 28, "carbs": 45, "fat": 26, "unit": "1 piece", "emoji": "🍔"},
    {"id": "chicken_burger", "name": "Chicken Burger", "category": "Fast Food", "calories": 450, "protein": 24, "carbs": 42, "fat": 22, "unit": "1 piece", "emoji": "🍔"},
    {"id": "beef_burger", "name": "Beef Burger", "category": "Fast Food", "calories": 480, "protein": 26, "carbs": 40, "fat": 24, "unit": "1 piece", "emoji": "🍔"},
    {"id": "double_patty_burger", "name": "Double Patty Burger", "category": "Fast Food", "calories": 650, "protein": 36, "carbs": 45, "fat": 35, "unit": "1 piece", "emoji": "🍔"},
    {"id": "pizza", "name": "Pizza", "category": "Fast Food", "calories": 266, "protein": 11, "carbs": 33, "fat": 10, "unit": "100g", "emoji": "🍕"},
    {"id": "pepperoni_pizza", "name": "Pepperoni Pizza", "category": "Fast Food", "calories": 290, "protein": 13, "carbs": 34, "fat": 13, "unit": "100g", "emoji": "🍕"},
    {"id": "fajita_pizza", "name": "Fajita Pizza", "category": "Fast Food", "calories": 275, "protein": 13, "carbs": 33, "fat": 11, "unit": "100g", "emoji": "🍕"},
    {"id": "cheese_pizza", "name": "Cheese Pizza", "category": "Fast Food", "calories": 270, "protein": 12, "carbs": 33, "fat": 11, "unit": "100g", "emoji": "🍕"},
    {"id": "fries", "name": "Fries", "category": "Fast Food", "calories": 312, "protein": 3, "carbs": 41, "fat": 15, "unit": "100g", "emoji": "🍟"},
    {"id": "chicken_wings", "name": "Chicken Wings", "category": "Fast Food", "calories": 290, "protein": 18, "carbs": 8, "fat": 21, "unit": "100g", "emoji": "🍗"},
    {"id": "nuggets", "name": "Nuggets", "category": "Fast Food", "calories": 295, "protein": 15, "carbs": 17, "fat": 19, "unit": "100g", "emoji": "🍗"},
    {"id": "hot_dog", "name": "Hot Dog", "category": "Fast Food", "calories": 290, "protein": 11, "carbs": 24, "fat": 17, "unit": "1 piece", "emoji": "🌭"},
    {"id": "sandwich", "name": "Sandwich", "category": "Fast Food", "calories": 250, "protein": 12, "carbs": 30, "fat": 9, "unit": "1 piece", "emoji": "🥪"},
    {"id": "club_sandwich", "name": "Club Sandwich", "category": "Fast Food", "calories": 400, "protein": 22, "carbs": 35, "fat": 19, "unit": "1 piece", "emoji": "🥪"},
    {"id": "pasta", "name": "Pasta", "category": "Fast Food", "calories": 220, "protein": 8, "carbs": 38, "fat": 5, "unit": "100g", "emoji": "🍝"},
    {"id": "lasagna", "name": "Lasagna", "category": "Fast Food", "calories": 290, "protein": 14, "carbs": 28, "fat": 14, "unit": "100g", "emoji": "🍝"},
    {"id": "mac_and_cheese", "name": "Mac and Cheese", "category": "Fast Food", "calories": 310, "protein": 12, "carbs": 36, "fat": 14, "unit": "100g", "emoji": "🧀"},
    {"id": "wrap", "name": "Wrap", "category": "Fast Food", "calories": 300, "protein": 15, "carbs": 35, "fat": 11, "unit": "1 piece", "emoji": "🌯"},
    {"id": "submarine_sandwich", "name": "Submarine Sandwich", "category": "Fast Food", "calories": 380, "protein": 20, "carbs": 42, "fat": 14, "unit": "1 piece", "emoji": "🥪"},
    {"id": "chicken_wrap", "name": "Chicken Wrap", "category": "Fast Food", "calories": 320, "protein": 18, "carbs": 34, "fat": 12, "unit": "1 piece", "emoji": "🌯"},
    {"id": "beef_wrap", "name": "Beef Wrap", "category": "Fast Food", "calories": 350, "protein": 20, "carbs": 34, "fat": 14, "unit": "1 piece", "emoji": "🌯"},
    {"id": "grilled_sandwich", "name": "Grilled Sandwich", "category": "Fast Food", "calories": 280, "protein": 14, "carbs": 30, "fat": 12, "unit": "1 piece", "emoji": "🥪"},
    {"id": "cheese_burger", "name": "Cheese Burger", "category": "Fast Food", "calories": 490, "protein": 26, "carbs": 42, "fat": 25, "unit": "1 piece", "emoji": "🍔"},
    {"id": "tower_burger", "name": "Tower Burger", "category": "Fast Food", "calories": 580, "protein": 30, "carbs": 46, "fat": 30, "unit": "1 piece", "emoji": "🍔"},
    {"id": "patty_burger", "name": "Patty Burger", "category": "Fast Food", "calories": 420, "protein": 22, "carbs": 40, "fat": 20, "unit": "1 piece", "emoji": "🍔"},
    {"id": "chicken_cheese_burger", "name": "Chicken Cheese Burger", "category": "Fast Food", "calories": 510, "protein": 27, "carbs": 44, "fat": 25, "unit": "1 piece", "emoji": "🍔"},
    {"id": "stuffed_crust_pizza", "name": "Stuffed Crust Pizza", "category": "Fast Food", "calories": 300, "protein": 13, "carbs": 36, "fat": 13, "unit": "100g", "emoji": "🍕"},
    {"id": "bbq_pizza", "name": "BBQ Pizza", "category": "Fast Food", "calories": 280, "protein": 13, "carbs": 34, "fat": 12, "unit": "100g", "emoji": "🍕"},
    {"id": "arabic_pizza", "name": "Arabic Pizza", "category": "Fast Food", "calories": 285, "protein": 13, "carbs": 34, "fat": 12, "unit": "100g", "emoji": "🍕"},
    {"id": "thin_crust_pizza", "name": "Thin Crust Pizza", "category": "Fast Food", "calories": 250, "protein": 11, "carbs": 30, "fat": 10, "unit": "100g", "emoji": "🍕"},
    {"id": "chicken_supreme_pizza", "name": "Chicken Supreme Pizza", "category": "Fast Food", "calories": 275, "protein": 13, "carbs": 33, "fat": 11, "unit": "100g", "emoji": "🍕"},
    {"id": "chicken_wings_bbq", "name": "Chicken Wings BBQ", "category": "Fast Food", "calories": 310, "protein": 19, "carbs": 10, "fat": 22, "unit": "100g", "emoji": "🍗"},
    {"id": "hot_wings", "name": "Hot Wings", "category": "Fast Food", "calories": 300, "protein": 18, "carbs": 9, "fat": 22, "unit": "100g", "emoji": "🍗"},
    {"id": "peri_peri_fries", "name": "Peri Peri Fries", "category": "Fast Food", "calories": 330, "protein": 4, "carbs": 43, "fat": 16, "unit": "1 serving", "emoji": "🍟"},
    {"id": "cheesy_fries", "name": "Cheesy Fries", "category": "Fast Food", "calories": 380, "protein": 8, "carbs": 44, "fat": 20, "unit": "1 serving", "emoji": "🍟"},
    {"id": "chicken_loaded_fries", "name": "Chicken Loaded Fries", "category": "Fast Food", "calories": 460, "protein": 18, "carbs": 46, "fat": 24, "unit": "1 serving", "emoji": "🍟"},
    {"id": "crunch_burger", "name": "Crunch Burger", "category": "Fast Food", "calories": 500, "protein": 26, "carbs": 44, "fat": 26, "unit": "1 piece", "emoji": "🍔"},
    {"id": "spicy_burger", "name": "Spicy Burger", "category": "Fast Food", "calories": 480, "protein": 25, "carbs": 43, "fat": 24, "unit": "1 piece", "emoji": "🍔"},
    {"id": "chicken_sub", "name": "Chicken Sub", "category": "Fast Food", "calories": 360, "protein": 20, "carbs": 40, "fat": 13, "unit": "1 piece", "emoji": "🥪"},
    {"id": "turkey_sandwich", "name": "Turkey Sandwich", "category": "Fast Food", "calories": 300, "protein": 18, "carbs": 30, "fat": 11, "unit": "1 piece", "emoji": "🥪"},
    {"id": "panini_sandwich", "name": "Panini Sandwich", "category": "Fast Food", "calories": 320, "protein": 15, "carbs": 35, "fat": 13, "unit": "1 piece", "emoji": "🥪"},
    {"id": "chicken_alfredo_pasta", "name": "Chicken Alfredo Pasta", "category": "Fast Food", "calories": 350, "protein": 18, "carbs": 36, "fat": 16, "unit": "100g", "emoji": "🍝"},
    {"id": "red_sauce_pasta", "name": "Red Sauce Pasta", "category": "Fast Food", "calories": 200, "protein": 8, "carbs": 36, "fat": 4, "unit": "100g", "emoji": "🍝"},
    {"id": "white_sauce_pasta", "name": "White Sauce Pasta", "category": "Fast Food", "calories": 260, "protein": 9, "carbs": 36, "fat": 10, "unit": "100g", "emoji": "🍝"},
    {"id": "spaghetti_bolognese", "name": "Spaghetti Bolognese", "category": "Fast Food", "calories": 250, "protein": 13, "carbs": 32, "fat": 8, "unit": "100g", "emoji": "🍝"},
    {"id": "fettuccine_alfredo", "name": "Fettuccine Alfredo", "category": "Fast Food", "calories": 290, "protein": 10, "carbs": 36, "fat": 13, "unit": "100g", "emoji": "🍝"},
    # Desserts
    {"id": "ras_malai", "name": "Ras Malai", "category": "Desserts & Sweets", "calories": 180, "protein": 6, "carbs": 24, "fat": 7, "unit": "1 piece", "emoji": "🍮"},
    {"id": "ladoo", "name": "Ladoo", "category": "Desserts & Sweets", "calories": 170, "protein": 3, "carbs": 28, "fat": 6, "unit": "1 piece", "emoji": "🍡"},
    {"id": "cham_cham", "name": "Cham Cham", "category": "Desserts & Sweets", "calories": 160, "protein": 4, "carbs": 28, "fat": 4, "unit": "1 piece", "emoji": "🍮"},
    {"id": "gajar_halwa", "name": "Gajar Halwa", "category": "Desserts & Sweets", "calories": 210, "protein": 4, "carbs": 30, "fat": 9, "unit": "100g", "emoji": "🍮"},
    {"id": "chocolate_brownie", "name": "Chocolate Brownie", "category": "Desserts & Sweets", "calories": 380, "protein": 4, "carbs": 50, "fat": 19, "unit": "100g", "emoji": "🍫"},
    {"id": "cheesecake", "name": "Cheesecake", "category": "Desserts & Sweets", "calories": 320, "protein": 5, "carbs": 28, "fat": 21, "unit": "100g", "emoji": "🍰"},
    {"id": "pudding", "name": "Pudding", "category": "Desserts & Sweets", "calories": 130, "protein": 3, "carbs": 20, "fat": 5, "unit": "100g", "emoji": "🍮"},
    {"id": "mousse", "name": "Mousse", "category": "Desserts & Sweets", "calories": 200, "protein": 3, "carbs": 22, "fat": 12, "unit": "100g", "emoji": "🍮"},
    {"id": "baklava", "name": "Baklava", "category": "Desserts & Sweets", "calories": 430, "protein": 6, "carbs": 42, "fat": 29, "unit": "100g", "emoji": "🍯"},
    {"id": "kunafa", "name": "Kunafa", "category": "Desserts & Sweets", "calories": 340, "protein": 7, "carbs": 42, "fat": 17, "unit": "100g", "emoji": "🧆"},
    {"id": "ice_cream", "name": "Ice Cream", "category": "Desserts & Sweets", "calories": 200, "protein": 3, "carbs": 24, "fat": 11, "unit": "1 scoop", "emoji": "🍦"},
    {"id": "chocolate_ice_cream", "name": "Chocolate Ice Cream", "category": "Desserts & Sweets", "calories": 220, "protein": 3, "carbs": 26, "fat": 12, "unit": "1 scoop", "emoji": "🍫"},
    {"id": "vanilla_ice_cream", "name": "Vanilla Ice Cream", "category": "Desserts & Sweets", "calories": 195, "protein": 3, "carbs": 24, "fat": 10, "unit": "1 scoop", "emoji": "🍦"},
    {"id": "strawberry_ice_cream", "name": "Strawberry Ice Cream", "category": "Desserts & Sweets", "calories": 190, "protein": 3, "carbs": 24, "fat": 10, "unit": "1 scoop", "emoji": "🍓"},
    {"id": "mango_ice_cream", "name": "Mango Ice Cream", "category": "Desserts & Sweets", "calories": 200, "protein": 3, "carbs": 26, "fat": 10, "unit": "1 scoop", "emoji": "🥭"},
    {"id": "custard", "name": "Custard", "category": "Desserts & Sweets", "calories": 120, "protein": 4, "carbs": 18, "fat": 4, "unit": "100g", "emoji": "🍮"},
    {"id": "shahi_tukray", "name": "Shahi Tukray", "category": "Desserts & Sweets", "calories": 280, "protein": 6, "carbs": 38, "fat": 12, "unit": "100g", "emoji": "🍮"},
    {"id": "seviyan", "name": "Seviyan", "category": "Desserts & Sweets", "calories": 190, "protein": 4, "carbs": 30, "fat": 7, "unit": "100g", "emoji": "🍮"},
    {"id": "rabri_falooda", "name": "Rabri Falooda", "category": "Desserts & Sweets", "calories": 280, "protein": 7, "carbs": 42, "fat": 10, "unit": "1 glass", "emoji": "🍹"},
    {"id": "chocolate_cake", "name": "Chocolate Cake", "category": "Desserts & Sweets", "calories": 350, "protein": 5, "carbs": 48, "fat": 16, "unit": "100g", "emoji": "🎂"},
    {"id": "red_velvet_cake", "name": "Red Velvet Cake", "category": "Desserts & Sweets", "calories": 360, "protein": 5, "carbs": 48, "fat": 18, "unit": "100g", "emoji": "🎂"},
    {"id": "black_forest_cake", "name": "Black Forest Cake", "category": "Desserts & Sweets", "calories": 340, "protein": 5, "carbs": 46, "fat": 16, "unit": "100g", "emoji": "🎂"},
    {"id": "donut", "name": "Donut", "category": "Desserts & Sweets", "calories": 280, "protein": 4, "carbs": 38, "fat": 14, "unit": "1 piece", "emoji": "🍩"},
    {"id": "cupcake", "name": "Cupcake", "category": "Desserts & Sweets", "calories": 250, "protein": 3, "carbs": 36, "fat": 12, "unit": "1 piece", "emoji": "🧁"},
    {"id": "swiss_roll", "name": "Swiss Roll", "category": "Desserts & Sweets", "calories": 310, "protein": 4, "carbs": 44, "fat": 13, "unit": "100g", "emoji": "🍰"},
    # Drinks
    {"id": "coca_cola", "name": "Coca Cola", "category": "Drinks", "calories": 42, "protein": 0, "carbs": 11, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "pepsi", "name": "Pepsi", "category": "Drinks", "calories": 41, "protein": 0, "carbs": 11, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "sprite", "name": "Sprite", "category": "Drinks", "calories": 38, "protein": 0, "carbs": 10, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "7up", "name": "7UP", "category": "Drinks", "calories": 38, "protein": 0, "carbs": 10, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "fanta", "name": "Fanta", "category": "Drinks", "calories": 45, "protein": 0, "carbs": 12, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "mountain_dew", "name": "Mountain Dew", "category": "Drinks", "calories": 54, "protein": 0, "carbs": 15, "fat": 0, "unit": "1 can (330ml)", "emoji": "🥤"},
    {"id": "mango_juice", "name": "Mango Juice", "category": "Drinks", "calories": 60, "protein": 0, "carbs": 15, "fat": 0, "unit": "1 glass", "emoji": "🥭"},
    {"id": "apple_juice", "name": "Apple Juice", "category": "Drinks", "calories": 50, "protein": 0, "carbs": 13, "fat": 0, "unit": "1 glass", "emoji": "🍎"},
    {"id": "orange_juice", "name": "Orange Juice", "category": "Drinks", "calories": 45, "protein": 1, "carbs": 10, "fat": 0, "unit": "1 glass", "emoji": "🍊"},
    {"id": "milkshake", "name": "Milkshake", "category": "Drinks", "calories": 230, "protein": 6, "carbs": 38, "fat": 7, "unit": "1 glass", "emoji": "🥛"},
    {"id": "cold_coffee", "name": "Cold Coffee", "category": "Drinks", "calories": 150, "protein": 4, "carbs": 22, "fat": 5, "unit": "1 glass", "emoji": "☕"},
    {"id": "black_coffee", "name": "Black Coffee", "category": "Drinks", "calories": 5, "protein": 0, "carbs": 1, "fat": 0, "unit": "1 cup", "emoji": "☕"},
    {"id": "latte", "name": "Latte", "category": "Drinks", "calories": 120, "protein": 6, "carbs": 12, "fat": 5, "unit": "1 cup", "emoji": "☕"},
    {"id": "cappuccino", "name": "Cappuccino", "category": "Drinks", "calories": 90, "protein": 5, "carbs": 8, "fat": 4, "unit": "1 cup", "emoji": "☕"},
    {"id": "smoothie", "name": "Smoothie", "category": "Drinks", "calories": 150, "protein": 3, "carbs": 30, "fat": 2, "unit": "1 glass", "emoji": "🥤"},
    {"id": "energy_drink", "name": "Energy Drink", "category": "Drinks", "calories": 110, "protein": 1, "carbs": 28, "fat": 0, "unit": "1 can", "emoji": "⚡"},
    {"id": "tea", "name": "Tea", "category": "Drinks", "calories": 35, "protein": 1, "carbs": 6, "fat": 1, "unit": "1 cup", "emoji": "🍵"},
    {"id": "green_tea", "name": "Green Tea", "category": "Drinks", "calories": 2, "protein": 0, "carbs": 0, "fat": 0, "unit": "1 cup", "emoji": "🍵"},
    {"id": "kashmiri_chai", "name": "Kashmiri Chai", "category": "Drinks", "calories": 120, "protein": 4, "carbs": 14, "fat": 6, "unit": "1 cup", "emoji": "🍵"},
    {"id": "lemonade", "name": "Lemonade", "category": "Drinks", "calories": 40, "protein": 0, "carbs": 11, "fat": 0, "unit": "1 glass", "emoji": "🍋"},
    {"id": "mint_margarita", "name": "Mint Margarita", "category": "Drinks", "calories": 50, "protein": 0, "carbs": 13, "fat": 0, "unit": "1 glass", "emoji": "🍹"},
    {"id": "chocolate_shake", "name": "Chocolate Shake", "category": "Drinks", "calories": 280, "protein": 7, "carbs": 42, "fat": 10, "unit": "1 glass", "emoji": "🍫"},
    {"id": "banana_shake", "name": "Banana Shake", "category": "Drinks", "calories": 260, "protein": 6, "carbs": 44, "fat": 8, "unit": "1 glass", "emoji": "🍌"},
    {"id": "strawberry_shake", "name": "Strawberry Shake", "category": "Drinks", "calories": 240, "protein": 6, "carbs": 40, "fat": 7, "unit": "1 glass", "emoji": "🍓"},
    # Fruits
    {"id": "apple", "name": "Apple", "category": "Fruits", "calories": 52, "protein": 0, "carbs": 14, "fat": 0, "unit": "1 medium", "emoji": "🍎"},
    {"id": "banana", "name": "Banana", "category": "Fruits", "calories": 89, "protein": 1, "carbs": 23, "fat": 0, "unit": "1 medium", "emoji": "🍌"},
    {"id": "mango", "name": "Mango", "category": "Fruits", "calories": 60, "protein": 1, "carbs": 15, "fat": 0, "unit": "100g", "emoji": "🥭"},
    {"id": "orange", "name": "Orange", "category": "Fruits", "calories": 47, "protein": 1, "carbs": 12, "fat": 0, "unit": "1 medium", "emoji": "🍊"},
    {"id": "guava", "name": "Guava", "category": "Fruits", "calories": 68, "protein": 3, "carbs": 14, "fat": 1, "unit": "1 medium", "emoji": "🍈"},
    {"id": "pomegranate", "name": "Pomegranate", "category": "Fruits", "calories": 83, "protein": 2, "carbs": 19, "fat": 1, "unit": "100g", "emoji": "🍎"},
    {"id": "watermelon", "name": "Watermelon", "category": "Fruits", "calories": 30, "protein": 1, "carbs": 8, "fat": 0, "unit": "100g", "emoji": "🍉"},
    {"id": "melon", "name": "Melon", "category": "Fruits", "calories": 34, "protein": 1, "carbs": 8, "fat": 0, "unit": "100g", "emoji": "🍈"},
    {"id": "grapes", "name": "Grapes", "category": "Fruits", "calories": 62, "protein": 1, "carbs": 17, "fat": 0, "unit": "100g", "emoji": "🍇"},
    {"id": "peach", "name": "Peach", "category": "Fruits", "calories": 39, "protein": 1, "carbs": 10, "fat": 0, "unit": "1 medium", "emoji": "🍑"},
    {"id": "pear", "name": "Pear", "category": "Fruits", "calories": 57, "protein": 0, "carbs": 15, "fat": 0, "unit": "1 medium", "emoji": "🍐"},
    {"id": "papaya", "name": "Papaya", "category": "Fruits", "calories": 43, "protein": 0, "carbs": 11, "fat": 0, "unit": "100g", "emoji": "🍈"},
    {"id": "dates", "name": "Dates", "category": "Fruits", "calories": 277, "protein": 2, "carbs": 75, "fat": 0, "unit": "100g", "emoji": "🟤"},
    {"id": "coconut", "name": "Coconut", "category": "Fruits", "calories": 354, "protein": 3, "carbs": 15, "fat": 33, "unit": "100g", "emoji": "🥥"},
    {"id": "kiwi", "name": "Kiwi", "category": "Fruits", "calories": 61, "protein": 1, "carbs": 15, "fat": 1, "unit": "1 medium", "emoji": "🥝"},
    {"id": "strawberry", "name": "Strawberry", "category": "Fruits", "calories": 32, "protein": 1, "carbs": 8, "fat": 0, "unit": "100g", "emoji": "🍓"},
    {"id": "blueberry", "name": "Blueberry", "category": "Fruits", "calories": 57, "protein": 1, "carbs": 14, "fat": 0, "unit": "100g", "emoji": "🫐"},
    {"id": "cherry", "name": "Cherry", "category": "Fruits", "calories": 50, "protein": 1, "carbs": 12, "fat": 0, "unit": "100g", "emoji": "🍒"},
    {"id": "apricot", "name": "Apricot", "category": "Fruits", "calories": 48, "protein": 1, "carbs": 11, "fat": 0, "unit": "100g", "emoji": "🍑"},
    {"id": "plum", "name": "Plum", "category": "Fruits", "calories": 46, "protein": 1, "carbs": 11, "fat": 0, "unit": "1 medium", "emoji": "🍑"},
    {"id": "lychee", "name": "Lychee", "category": "Fruits", "calories": 66, "protein": 1, "carbs": 17, "fat": 0, "unit": "100g", "emoji": "🍈"},
    {"id": "fig", "name": "Fig", "category": "Fruits", "calories": 74, "protein": 1, "carbs": 19, "fat": 0, "unit": "100g", "emoji": "🫐"},
    {"id": "dragon_fruit", "name": "Dragon Fruit", "category": "Fruits", "calories": 60, "protein": 1, "carbs": 13, "fat": 0, "unit": "100g", "emoji": "🍈"},
    {"id": "jackfruit", "name": "Jackfruit", "category": "Fruits", "calories": 95, "protein": 2, "carbs": 23, "fat": 1, "unit": "100g", "emoji": "🍈"},
    {"id": "passion_fruit", "name": "Passion Fruit", "category": "Fruits", "calories": 97, "protein": 2, "carbs": 23, "fat": 1, "unit": "100g", "emoji": "🍈"},
    # Vegetables
    {"id": "cucumber", "name": "Cucumber", "category": "Vegetables", "calories": 16, "protein": 1, "carbs": 4, "fat": 0, "unit": "100g", "emoji": "🥒"},
    {"id": "tomato", "name": "Tomato", "category": "Vegetables", "calories": 18, "protein": 1, "carbs": 4, "fat": 0, "unit": "100g", "emoji": "🍅"},
    {"id": "carrot", "name": "Carrot", "category": "Vegetables", "calories": 41, "protein": 1, "carbs": 10, "fat": 0, "unit": "100g", "emoji": "🥕"},
    {"id": "onion", "name": "Onion", "category": "Vegetables", "calories": 40, "protein": 1, "carbs": 9, "fat": 0, "unit": "100g", "emoji": "🧅"},
    {"id": "capsicum", "name": "Capsicum", "category": "Vegetables", "calories": 31, "protein": 1, "carbs": 6, "fat": 0, "unit": "100g", "emoji": "🫑"},
    {"id": "spinach", "name": "Spinach", "category": "Vegetables", "calories": 23, "protein": 3, "carbs": 4, "fat": 0, "unit": "100g", "emoji": "🥬"},
    {"id": "lettuce", "name": "Lettuce", "category": "Vegetables", "calories": 15, "protein": 1, "carbs": 3, "fat": 0, "unit": "100g", "emoji": "🥬"},
    {"id": "cabbage", "name": "Cabbage", "category": "Vegetables", "calories": 25, "protein": 1, "carbs": 6, "fat": 0, "unit": "100g", "emoji": "🥬"},
    {"id": "broccoli", "name": "Broccoli", "category": "Vegetables", "calories": 34, "protein": 3, "carbs": 7, "fat": 0, "unit": "100g", "emoji": "🥦"},
    {"id": "cauliflower", "name": "Cauliflower", "category": "Vegetables", "calories": 25, "protein": 2, "carbs": 5, "fat": 0, "unit": "100g", "emoji": "🥦"},
    {"id": "corn", "name": "Corn", "category": "Vegetables", "calories": 86, "protein": 3, "carbs": 19, "fat": 1, "unit": "100g", "emoji": "🌽"},
    {"id": "peas", "name": "Peas", "category": "Vegetables", "calories": 81, "protein": 5, "carbs": 14, "fat": 0, "unit": "100g", "emoji": "🫛"},
    {"id": "beans", "name": "Beans", "category": "Vegetables", "calories": 31, "protein": 2, "carbs": 7, "fat": 0, "unit": "100g", "emoji": "🫘"},
    {"id": "sweet_potato", "name": "Sweet Potato", "category": "Vegetables", "calories": 86, "protein": 2, "carbs": 20, "fat": 0, "unit": "100g", "emoji": "🍠"},
    {"id": "potato", "name": "Potato", "category": "Vegetables", "calories": 77, "protein": 2, "carbs": 17, "fat": 0, "unit": "100g", "emoji": "🥔"},
    {"id": "turnip", "name": "Turnip", "category": "Vegetables", "calories": 28, "protein": 1, "carbs": 6, "fat": 0, "unit": "100g", "emoji": "🥔"},
    {"id": "garlic", "name": "Garlic", "category": "Vegetables", "calories": 149, "protein": 6, "carbs": 33, "fat": 1, "unit": "100g", "emoji": "🧄"},
    {"id": "ginger", "name": "Ginger", "category": "Vegetables", "calories": 80, "protein": 2, "carbs": 18, "fat": 1, "unit": "100g", "emoji": "🫚"},
    {"id": "radish", "name": "Radish", "category": "Vegetables", "calories": 16, "protein": 1, "carbs": 3, "fat": 0, "unit": "100g", "emoji": "🌱"},
    {"id": "pumpkin", "name": "Pumpkin", "category": "Vegetables", "calories": 26, "protein": 1, "carbs": 7, "fat": 0, "unit": "100g", "emoji": "🎃"},
    # Snacks
    {"id": "lays_chips", "name": "Lays Chips", "category": "Snacks", "calories": 536, "protein": 7, "carbs": 53, "fat": 35, "unit": "1 pack (30g)", "emoji": "🥔"},
    {"id": "kurkure", "name": "Kurkure", "category": "Snacks", "calories": 520, "protein": 6, "carbs": 56, "fat": 30, "unit": "1 pack (30g)", "emoji": "🌽"},
    {"id": "slanty", "name": "Slanty", "category": "Snacks", "calories": 510, "protein": 6, "carbs": 55, "fat": 30, "unit": "1 pack (30g)", "emoji": "🥔"},
    {"id": "popcorn", "name": "Popcorn", "category": "Snacks", "calories": 375, "protein": 11, "carbs": 74, "fat": 4, "unit": "100g", "emoji": "🍿"},
    {"id": "biscuits", "name": "Biscuits", "category": "Snacks", "calories": 420, "protein": 6, "carbs": 68, "fat": 14, "unit": "100g", "emoji": "🍪"},
    {"id": "chocolate", "name": "Chocolate", "category": "Snacks", "calories": 546, "protein": 5, "carbs": 60, "fat": 31, "unit": "100g", "emoji": "🍫"},
    {"id": "candy", "name": "Candy", "category": "Snacks", "calories": 394, "protein": 0, "carbs": 98, "fat": 0, "unit": "100g", "emoji": "🍬"},
    {"id": "cake_rusk", "name": "Cake Rusk", "category": "Snacks", "calories": 380, "protein": 7, "carbs": 65, "fat": 10, "unit": "100g", "emoji": "🍞"},
    {"id": "nimco", "name": "Nimco", "category": "Snacks", "calories": 480, "protein": 10, "carbs": 55, "fat": 26, "unit": "100g", "emoji": "🥜"},
    {"id": "trail_mix", "name": "Trail Mix", "category": "Snacks", "calories": 462, "protein": 12, "carbs": 45, "fat": 28, "unit": "100g", "emoji": "🥜"},
    {"id": "energy_bar", "name": "Energy Bar", "category": "Snacks", "calories": 380, "protein": 10, "carbs": 55, "fat": 14, "unit": "1 bar", "emoji": "⚡"},
    {"id": "protein_bar", "name": "Protein Bar", "category": "Snacks", "calories": 360, "protein": 20, "carbs": 40, "fat": 12, "unit": "1 bar", "emoji": "💪"},
    {"id": "ice_cream_cone", "name": "Ice Cream Cone", "category": "Snacks", "calories": 230, "protein": 4, "carbs": 32, "fat": 10, "unit": "1 cone", "emoji": "🍦"},
    {"id": "cookies", "name": "Cookies", "category": "Snacks", "calories": 480, "protein": 5, "carbs": 65, "fat": 24, "unit": "100g", "emoji": "🍪"},
    {"id": "crackers", "name": "Crackers", "category": "Snacks", "calories": 420, "protein": 8, "carbs": 68, "fat": 14, "unit": "100g", "emoji": "🫙"},
    {"id": "pretzels", "name": "Pretzels", "category": "Snacks", "calories": 380, "protein": 9, "carbs": 80, "fat": 4, "unit": "100g", "emoji": "🥨"},
    {"id": "peanuts", "name": "Peanuts", "category": "Snacks", "calories": 567, "protein": 26, "carbs": 16, "fat": 49, "unit": "100g", "emoji": "🥜"},

]

CATEGORY_EMOJIS = {
    "Rice & Biryani": "🍚", "Bread & Roti": "🫓", "Curries & Daal": "🍲",
    "BBQ & Grilled": "🍢", "Snacks & Street Food": "🥟", "Desserts & Sweets": "🍮",
    "Drinks": "☕", "Custom": "⭐"
}

def get_today():
    return date.today().isoformat()

def all_foods():
    custom = CustomFood.query.all()
    custom_list = [{
        "id": f.id, "name": f.name, "category": f.category,
        "calories": f.calories, "protein": f.protein,
        "carbs": f.carbs, "fat": f.fat,
        "unit": f.unit, "emoji": f.emoji, "is_custom": True
    } for f in custom]
    return FOOD_DB + custom_list

# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/foods")
def get_foods():
    query    = request.args.get("q", "").lower()
    category = request.args.get("category", "")
    foods = all_foods()
    if query:    foods = [f for f in foods if query in f["name"].lower()]
    if category: foods = [f for f in foods if f["category"] == category]
    return jsonify(foods)

@app.route("/api/categories")
def get_categories():
    custom_cats = [f.category for f in CustomFood.query.all()]
    all_cats = sorted(set(f["category"] for f in FOOD_DB) | set(custom_cats))
    return jsonify(all_cats)

@app.route("/api/foods/custom", methods=["POST"])
def add_custom_food():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    category = data.get("category", "Custom")
    emoji = CATEGORY_EMOJIS.get(category, "⭐")

    food = CustomFood(
        id       = "custom_" + str(uuid.uuid4())[:8],
        name     = name,
        category = category,
        calories = int(data.get("calories", 0)),
        protein  = float(data.get("protein", 0)),
        carbs    = float(data.get("carbs", 0)),
        fat      = float(data.get("fat", 0)),
        unit     = data.get("unit", "100g").strip(),
        emoji    = emoji,
    )
    db.session.add(food)
    db.session.commit()
    return jsonify({"id": food.id, "name": food.name, "message": "Food added!"}), 201

@app.route("/api/foods/custom/<food_id>", methods=["DELETE"])
def delete_custom_food(food_id):
    food = CustomFood.query.get(food_id)
    if not food:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(food)
    db.session.commit()
    return jsonify({"deleted": food_id})

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

    food = next((f for f in all_foods() if f["id"] == food_id), None)
    if not food:
        return jsonify({"error": "Food not found"}), 404

    entry = FoodLog(
        id       = str(uuid.uuid4())[:8],
        date     = day, meal = meal, food_id = food_id,
        name     = food["name"], emoji = food["emoji"],
        quantity = qty, unit = food["unit"],
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
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)