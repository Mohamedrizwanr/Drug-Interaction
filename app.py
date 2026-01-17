from flask import Flask, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import json

# ---- Project services ----
from services.drug_mapper import get_id, autocomplete
from services.inference_service import predict
from services.side_effect_service import get_side_effects
from services.risk_service import risk
from services.explanation_service import explain_side_effect


# =====================================================
# CREATE FLASK APP
# =====================================================
app = Flask(__name__)
app.secret_key = "secure_key"


# =====================================================
# DATABASE CONNECTION
# =====================================================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="drug_interaction_db"
)


# =====================================================
# ENTRY PAGE (LOGIN / SIGNUP / GUEST)
# =====================================================
@app.route("/")
def index():
    return render_template("index.html")


# =====================================================
# SIGNUP
# =====================================================
from mysql.connector import IntegrityError

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            db.commit()
            return redirect("/login")

        except IntegrityError:
            error = "Email already registered. Please login instead."

    return render_template("signup.html", error=error)



# =====================================================
# LOGIN (EMAIL + PASSWORD)
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/home")

        return "Invalid email or password"

    return render_template("login.html")


# =====================================================
# GUEST ACCESS
# =====================================================
@app.route("/guest")
def guest():
    session.clear()
    session["guest"] = True
    return redirect("/home")


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================================================
# HOME PAGE (PROTECTED)
# =====================================================
@app.route("/home")
def home():
    if "user_id" not in session and "guest" not in session:
        return redirect("/")
    return render_template("home.html")


# =====================================================
# AUTOCOMPLETE API
# =====================================================
@app.route("/autocomplete")
def auto():
    q = request.args.get("q", "")
    return jsonify(autocomplete(q))


# =====================================================
# PREDICT API (CORE FUNCTIONALITY)
# =====================================================
@app.route("/predict", methods=["POST"])
def predict_route():

    # 1️⃣ USER TYPE
    is_logged_in = "user_id" in session

    # 2️⃣ INPUT
    data = request.json.get("medicines", "")
    names = [n.strip() for n in data.split(",")]

    drug_ids = []
    name_map = {}

    for n in names:
        did = get_id(n)
        if did:
            drug_ids.append(did)
            name_map[did] = n

    # 3️⃣ INFERENCE
    predictions = predict(drug_ids)
    output = []

    for p in predictions:
        score, level = risk(p["probability"])
        side_effects = get_side_effects(p["drug1"], p["drug2"])

        formatted = []
        for s in side_effects:
            formatted.append({
                "name": s["name"],
                "severity": s["severity"],
                "explanation": explain_side_effect(
                    s["name"], s["severity"]
                )
            })

        output.append({
            "pair": f"{name_map[p['drug1']]} + {name_map[p['drug2']]}",
            "risk_score": score,
            "severity": level,
            "side_effects": formatted
        })

    # 4️⃣ SAVE HISTORY (LOGGED-IN USERS ONLY)
    if is_logged_in:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO search_history (user_id, drugs, result) VALUES (%s, %s, %s)",
            (session["user_id"], data, json.dumps(output))
        )
        db.commit()

    # 5️⃣ RETURN RESULT
    return jsonify(output)


# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
