import datetime
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import os
import uuid
from flask import flash
from functools import wraps
from utils import check_password, hash_password
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://rabiasahincs:G075cFEiv6gjHLiJ@assignment1.lvx4kdh.mongodb.net/?retryWrites=true&w=majority&appName=assignment1")
client = MongoClient(MONGO_URI)
db = client["assignment1"]

items_collection = db.items
users_collection = db.users

app = Flask(__name__)
app.secret_key = 'secret-key'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = users_collection.find_one({"user_id": user_id})
        if not user or not user.get("is_admin"):
            return "Unauthorized", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    search = request.args.get('search')
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort = request.args.get('sort')
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = category
    price_query = {}
    if min_price:
        try:
            price_query["$gte"] = float(min_price)
        except ValueError:
            pass
    if max_price:
        try:
            price_query["$lte"] = float(max_price)
        except ValueError:
            pass
    if price_query:
        query["price"] = price_query

    sort_order = None
    if sort == "price_asc":
        sort_order = [("price", 1)]
    elif sort == "price_desc":
        sort_order = [("price", -1)]
    elif sort == "popular":
        sort_order = [("rating", -1)]

    if sort_order:
        cursor = items_collection.find(query).sort(sort_order)
    else:
        cursor = items_collection.find(query)

    items_list = []
    for item in cursor:
        if "_id" in item:
            item["_id"] = str(item["_id"])
        item["rating"] = item.get("rating", 0)
        items_list.append(item)

    return render_template("home.html", items=items_list)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for('register'))

        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)
        new_user = {
            "user_id": user_id,
            "username": username,
            "password": hashed_pw,
            "is_admin": False
        }
        users_collection.insert_one(new_user)
        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users_collection.find_one({"username": username})
        
        if user:
            if check_password(password, user.get("password")):
                session["user_id"] = user.get("user_id")
                session["username"] = username
                session["is_admin"] = user.get("is_admin", False)
                return redirect(url_for('home'))
            else:
                flash("Incorrect password. Please try again.", "danger")
        else:
            flash("User not found. Please check your username.", "danger")
        
        return redirect(url_for('login'))
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for('home'))

@app.route("/item/<item_id>", methods=["GET"])
def item_detail(item_id):
    item = items_collection.find_one({"item_id": item_id})
    if not item:
        return "Item not found", 404
    
    dynamic_rating = calculate_average_rating(item_id)
    item["rating"] = dynamic_rating
    
    enriched_reviews = []
    for review in item.get("reviews", []):
        user = users_collection.find_one({"user_id": review["user_id"]})
        enriched_reviews.append({
            "username": user["username"] if user else "Unknown User",
            "review_text": review.get("review_text", ""),
            "rating": next(
                (r["score"] for r in item.get("ratings", []) 
                 if r["user_id"] == review["user_id"]),
                None
            ),
            "created_at": review.get("created_at", "N/A")
        })
    
    return render_template("item_detail.html", item=item, reviews=enriched_reviews)
@app.route("/item/<item_id>/rate-review", methods=["POST"])
@login_required
def rate_review_item(item_id):
    try:
        user_id = session.get("user_id")
        rating_value = request.form.get("rating")
        review_text = request.form.get("review")
        
        if rating_value:
            rating_value = int(rating_value)
            items_collection.update_one(
                {"item_id": item_id},
                {"$pull": {"ratings": {"user_id": user_id}}}
            )
            
            items_collection.update_one(
                {"item_id": item_id},
                {"$push": {"ratings": {"user_id": user_id, "score": rating_value}}}
            )
            recalc_item_rating(item_id)
        
        if review_text:
            items_collection.update_one(
                {"item_id": item_id},
                {"$pull": {"reviews": {"user_id": user_id}}}
            )
            
            items_collection.update_one(
                {"item_id": item_id},
                {"$push": {
                    "reviews": {
                        "user_id": user_id,
                        "review_text": review_text,
                    }
                }}
            )
        
    except Exception as e:
        return f"Error: {str(e)}", 500
    return redirect(url_for('item_detail', item_id=item_id))


def recalc_item_rating(item_id):
    pipeline = [
        {"$match": {"item_id": item_id}},
        {"$unwind": "$ratings"},
        {"$group": {"_id": None, "avgRating": {"$avg": "$ratings.score"}}}
    ]
    result = list(items_collection.aggregate(pipeline))
    new_rating = result[0]["avgRating"] if result else 0
    items_collection.update_one({"item_id": item_id}, {"$set": {"rating": new_rating}})
    return new_rating

    return new_rating

@app.route("/update_rating/<item_id>", methods=["POST"])
def update_rating(item_id):
    new_rating = recalc_item_rating(item_id)
    return jsonify({"new_rating": new_rating})

def calculate_average_rating(item_id):
    item = items_collection.find_one({"item_id": item_id})
    if not item or not item.get("ratings"):
        return 0

    valid_ratings = []
    for rating in item["ratings"]:
        user_id = rating.get("user_id")
        if user_id and users_collection.find_one({"user_id": user_id}):
            valid_ratings.append(rating["score"])

    if not valid_ratings:
        return 0

    return sum(valid_ratings) / len(valid_ratings)

@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return redirect(url_for("login"))
    username = user["username"]
    
    items_cursor = items_collection.find({
        "$or": [{"ratings.user_id": user_id}, {"reviews.user_id": user_id}]
    })
    
    total_rating = 0
    rating_count = 0
    reviews_list = []
    
    for item in items_cursor:
        user_ratings = [r["score"] for r in item.get("ratings", []) if r["user_id"] == user_id]
        if user_ratings:
            total_rating += sum(user_ratings)
            rating_count += len(user_ratings)
        
        for review in item.get("reviews", []):
            if review["user_id"] == user_id:
                rating_value = next(
                    (r["score"] for r in item.get("ratings", []) if r["user_id"] == user_id),
                    0
                )
                reviews_list.append({
                    "item_name": item.get("name", "Unknown Item"),
                    "review": review.get("review_text", ""),
                    "rating": rating_value,
                    "created_at": review.get("created_at", "N/A")
                })
                
    average_rating = total_rating / rating_count if rating_count > 0 else 0
    
    return render_template("profile.html", username=username, average_rating=average_rating, reviews=reviews_list)


@app.route("/admin/panel", methods=["GET", "POST"])
@login_required
@admin_required
def admin_panel():
    section = request.args.get("section", None)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "remove_item":
            item_ids = request.form.getlist("item_ids")
            if item_ids:
                items_collection.delete_many({"item_id": {"$in": item_ids}})
            return redirect(url_for("admin_panel", section="remove_item"))

        elif action == "remove_user":
            user_ids = request.form.getlist("user_ids")
            if user_ids:
                users_collection.delete_many({"user_id": {"$in": user_ids}})
                items_collection.update_many(
                    {},
                    {
                        "$pull": {
                            "ratings": {"user_id": {"$in": user_ids}},
                            "reviews": {"user_id": {"$in": user_ids}}
                        }
                    }
                )
                affected_items = items_collection.find({"ratings.user_id": {"$in": user_ids}})
                for item in affected_items:
                    recalc_item_rating(item["item_id"])
            return redirect(url_for("admin_panel", section="remove_user"))

        elif action == "add_item":
            name = request.form.get("name")
            description = request.form.get("description")
            try:
                price = float(request.form.get("price", 0))
            except ValueError:
                price = 0.0
            seller = request.form.get("seller")
            image = request.form.get("image")
            category = request.form.get("category")

            extra_fields = {}
            battery_life = request.form.get("battery_life", "")
            age = request.form.get("age", "")
            size = request.form.get("size", "")
            material = request.form.get("material", "")

            if category == "GPS Sport Watches" and battery_life:
                extra_fields["battery_life"] = battery_life
            if category in ["Antique Furniture", "Vinyls"] and age:
                extra_fields["age"] = age
            if category == "Running Shoes" and size:
                extra_fields["size"] = size
            if (category == "Antique Furniture" or category == "Running Shoes") and material:
                extra_fields["material"] = material

            new_item = {
                "item_id": str(uuid.uuid4()),
                "name": name,
                "description": description,
                "price": price,
                "seller": seller,
                "image": image,
                "category": category,
                "rating": 0,
                "ratings": [],
                "reviews": []
            }
            new_item.update(extra_fields)
            items_collection.insert_one(new_item)

            return redirect(url_for("admin_panel", section="add_item"))

        elif action == "add_user":
            username = request.form.get("username")
            password = request.form.get("password")

            if not users_collection.find_one({"username": username}):
                hashed_pw = hash_password(password)
                new_user = {
                    "user_id": str(uuid.uuid4()),
                    "username": username,
                    "password": hashed_pw,
                    "is_admin": False
                }
                users_collection.insert_one(new_user)
                
            else:
                flash(f"Username '{username}' already exists.", "danger")

            return redirect(url_for("admin_panel", section="add_user"))

    items = []
    users = []
    if section == "remove_item":
        items = list(items_collection.find())
    if section == "remove_user":
        users = list(users_collection.find({"is_admin": False}))

    return render_template(
        "admin_panel.html",
        section=section,
        items=items,
        users=users
    )

def handler(request, context):
    return app(request.environ, lambda status, headers: (status, headers))

app.handler = handler

if __name__ == "__main__":
    if not users_collection.find_one({"username": "admin"}):
        admin_id = str(uuid.uuid4())
        admin_pw = os.getenv("ADMIN_PASSWORD", "adminpass")
        hashed_admin_pw = hash_password(admin_pw)
        admin_user = {
            "user_id": admin_id,
            "username": "admin",
            "password": hashed_admin_pw,
            "is_admin": True
        }
        users_collection.insert_one(admin_user)
    app.run(debug=True)