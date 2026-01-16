from flask import Flask, request, jsonify, render_template, session
from services.drug_mapper import get_id, autocomplete
from services.inference_service import predict
from services.side_effect_service import get_side_effects
from services.risk_service import risk
from services.explanation_service import explain_side_effect
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import json



# ---------------- CREATE FLASK APP FIRST ----------------
app = Flask(__name__)
app.secret_key = "secure_key"

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="drug_interaction_db"
)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("home.html")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/autocomplete")
def auto():
    q = request.args.get("q", "")
    return jsonify(autocomplete(q))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()

        return redirect("/login")

    return render_template("signup.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/home")

        return "Invalid email or password"

    return render_template("login.html")
@app.route("/guest")
def guest():
    session.clear()
    session["guest"] = True
    return redirect("/home")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/predict", methods=["POST"])
def predict_route():

    # =====================================================
    # 🔹 1️⃣ CHECK USER TYPE (ADD THIS AT THE VERY TOP)
    # =====================================================
    is_logged_in = "user_id" in session
    is_guest = session.get("guest", False)

    # =====================================================
    # 🔹 2️⃣ GET USER INPUT (EXISTING CODE – KEEP)
    # =====================================================
    data = request.json.get("medicines", "")
    names = [n.strip() for n in data.split(",")]

    drug_ids = []
    name_map = {}

    for n in names:
        did = get_id(n)
        if did:
            drug_ids.append(did)
            name_map[did] = n

    # =====================================================
    # 🔹 3️⃣ RUN GNN INFERENCE (EXISTING CODE – KEEP)
    # =====================================================
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

    # =====================================================
    # 🔹 4️⃣ SAVE HISTORY (ADD HERE – AFTER OUTPUT READY)
    # =====================================================
    if is_logged_in:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO search_history (user_id, drugs, result) VALUES (%s, %s, %s)",
            (
                session["user_id"],
                data,                # original medicine names
                json.dumps(output)   # final result
            )
        )
        db.commit()

    # =====================================================
    # 🔹 5️⃣ RETURN RESULT (EXISTING CODE – KEEP)
    # =====================================================
    return jsonify(output)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)

