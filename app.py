import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from urllib.parse import quote_plus
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- Configuration ----------
app = Flask(__name__)
app.secret_key = "healbot_secret_key"

# MongoDB Atlas credentials
username = quote_plus("Utkarsh977")
password = quote_plus("Utkarsh1234")
app.config["MONGO_URI"] = f"mongodb+srv://{username}:{password}@utkarsh.2ru1s.mongodb.net/healbot?retryWrites=true&w=majority"

mongo = PyMongo(app)
appointments = mongo.db.appointments
contacts = mongo.db.contacts
users = mongo.db.users

try:
    mongo.cx.server_info()
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

# ---------- Doctor Data ----------
DOCTORS = [
    "Dr. Amit - General Physician",
    "Dr. Priya - Pediatrician",
    "Dr. Kaur - Dermatologist",
    "Dr. Ramesh - Cardiologist",
    "Dr. Mehta - Orthopedic"
]

# ---------- Local Chatbot Knowledge Base ----------
FAQS = [
    {"q": r"(hi|hello|hey)", "a": "Hello! 👋 I’m HealBot. How are you feeling today?"},
    {"q": r"who (are|r) you", "a": "I’m HealBot, your AI health companion 🤖. I can help you with diseases, medicines, and doctor appointments."},
    {"q": r"fever", "a": "For fever, take rest, drink plenty of fluids, and you may take paracetamol if the fever is high."},
    {"q": r"headache", "a": "Headaches can be due to stress or dehydration. Drink water and rest. Consult a doctor if persistent."},
    {"q": r"cold|cough", "a": "For cold or cough, drink warm fluids, use steam, and take rest. If symptoms persist, see a doctor."},
    {"q": r"asthma", "a": "Asthma causes breathing difficulty. Use your inhaler as prescribed and avoid dust and smoke."},
    {"q": r"diabetes", "a": "Diabetes is caused by high blood sugar. Control it with diet, exercise, and regular checkups."},
    {"q": r"hypertension|blood pressure", "a": "Hypertension is high blood pressure. Reduce salt intake, avoid stress, and exercise regularly."},
    {"q": r"malaria", "a": "Malaria is spread by mosquitoes. Symptoms include fever, chills, and sweating. Consult a doctor immediately."},
    {"q": r"dengue", "a": "Dengue is caused by mosquito bites. Drink fluids and rest. Seek medical help if fever or rashes appear."},
    {"q": r"toothache", "a": "For toothache, rinse with warm salt water and visit a dentist if pain continues."},
    {"q": r"stomach pain", "a": "Stomach pain can have many causes. Eat light food and drink water. If severe, consult a doctor."},
    {"q": r"medicine|tablet", "a": "Please tell me the name of the medicine, and I can give you more details."},
    {"q": r"appointment|book|consult", "a": "You can easily book an appointment on our 'Book Appointment' page."},
    {"q": r"emergency", "a": "In an emergency, please contact your nearest hospital or call 108 immediately."},
    {"q": r"covid|corona", "a": "COVID-19 causes fever, cough, and breathing issues. Isolate yourself and get tested if you have symptoms."},
    {"q": r"skin|rash|itch", "a": "Skin issues can be allergic reactions. Keep the area clean and consult a dermatologist if it spreads."},
    {"q": r"eye pain|vision|eye", "a": "Eye strain can be from screens. Rest your eyes and see an eye specialist if pain continues."},
    {"q": r"back pain", "a": "Back pain often results from posture or strain. Apply a hot compress and rest. If severe, consult a doctor."},
    {"q": r"heart attack|chest pain", "a": "Chest pain can be serious. Please seek emergency medical care immediately."},
    {"q": r"thank|thanks", "a": "You're most welcome! 😊 Take care of your health."},
    {"q": r"bye", "a": "Goodbye! 👋 Stay safe and healthy."}
]

# ---------- Chatbot Logic ----------
def bot_response(user_text):
    text = user_text.lower().strip()

    for item in FAQS:
        if re.search(item["q"], text):
            return {"reply": item["a"], "source": "faq"}

    # Default fallback
    return {"reply": "🤔 I’m not sure about that one. Try asking like: 'Symptoms of malaria' or 'Treatment for diabetes'.", "source": "fallback"}

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", doctors=DOCTORS)

@app.route("/library")
def library():
    topics = [
        {"title": "Common Cold", "summary": "Viral infection causing sneezing and sore throat.", "detail": "Rest and fluids help recovery.", "image": "cold.jpg"},
        {"title": "Hypertension", "summary": "High blood pressure that can damage organs.", "detail": "Reduce salt intake and monitor regularly.", "image": "hypertension.jpg"},
        {"title": "Diabetes", "summary": "High blood sugar due to insulin imbalance.", "detail": "Diet control and exercise are key.", "image": "diabetes.jpg"},
        {"title": "Asthma", "summary": "Chronic breathing issue causing wheezing.", "detail": "Use inhalers as prescribed and avoid triggers.", "image": "asthma.jpg"},
        {"title": "Dengue", "summary": "Mosquito-borne fever causing pain and rashes.", "detail": "Stay hydrated and get medical attention.", "image": "dengue.jpg"}
    ]
    return render_template("library.html", topics=topics)

@app.route("/book", methods=["GET", "POST"])
def book():
    if "user_email" not in session:
        flash("Please log in to book an appointment.", "warning")
        return redirect(url_for("login"))

    user_email = session["user_email"]

    if request.method == "POST":
        name = request.form.get("name")
        doctor = request.form.get("doctor")
        date = request.form.get("date")
        time = request.form.get("time")

        if not all([name, doctor, date, time]):
            flash("Please fill all fields", "danger")
            return redirect(url_for("book"))

        appointment_data = {
            "user_email": user_email,
            "name": name,
            "doctor": doctor,
            "date": date,
            "time": time,
            "created_at": datetime.utcnow()
        }
        appointments.insert_one(appointment_data)
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("book"))

    all_appointments = list(appointments.find({"user_email": user_email}).sort("created_at", -1))
    return render_template("appointment.html", doctors=DOCTORS, appts=all_appointments)

@app.route("/delete_appointment/<id>", methods=["POST"])
def delete_appointment(id):
    appointments.delete_one({"_id": ObjectId(id)})
    flash("Appointment deleted successfully!", "info")
    return redirect(url_for("book"))

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    contact_data = {
        "name": name,
        "email": email,
        "message": message,
        "sent_at": datetime.utcnow()
    }
    contacts.insert_one(contact_data)
    return jsonify({"status": "success", "message": "Message received successfully!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_text = data.get("message", "")
    print(f"💬 User said: {user_text}")  # Debug log

    if not user_text:
        return jsonify({"reply": "Please type your question.", "ok": False})

    resp = bot_response(user_text)
    return jsonify({"reply": resp["reply"], "ok": True, "source": resp["source"]})

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if users.find_one({"email": email}):
            flash("Email already registered!", "danger")
            return redirect(url_for("signup"))

        hashed_pw = generate_password_hash(password)
        users.insert_one({"name": name, "email": email, "password": hashed_pw})
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_email"] = email
            flash("Login successful!", "success")
            return redirect(url_for("book"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
