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
    {"q": r"(what|which).*covid|coronavirus", "a": "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus."},
    {"q": r"fever|temperature", "a": "Fever is usually a sign of infection. Stay hydrated and consult a doctor if it lasts more than 48 hours."},
    {"q": r"headache", "a": "Headaches may occur due to stress, dehydration, or infection. Rest and fluids help."},
    {"q": r"toothache", "a": "Rinse with warm salt water. If the pain persists, consult a dentist."},
    {"q": r"cold|sneeze|runny nose", "a": "Common cold is viral. Rest, steam inhalation, and hydration help."},
    {"q": r"cough", "a": "Cough can be dry or wet. Honey water, steam, and warm fluids help."},
    {"q": r"flu|influenza", "a": "Flu is a viral infection. Rest, fluids, and paracetamol may help."},
    {"q": r"sore throat", "a": "Salt-water gargles and warm fluids help soothe a sore throat."},
    {"q": r"throat pain", "a": "Warm salt-water gargles and rest can reduce throat pain."},
    {"q": r"stomach pain|abdominal pain", "a": "Avoid heavy meals. If pain is severe or persistent, consult a doctor."},
    {"q": r"gas|bloating", "a": "Ginger tea, light meals, and walking can relieve gas."},
    {"q": r"vomit|vomiting|nausea", "a": "Drink ORS to avoid dehydration. Seek help if vomiting is continuous."},
    {"q": r"diarrhea|loose motion", "a": "Hydrate with ORS and avoid heavy or oily foods."},
    {"q": r"constipation", "a": "Increase fiber intake and drink warm water regularly."},
    {"q": r"acidity|heartburn", "a": "Avoid spicy foods. Cold milk or antacids may help."},
    {"q": r"allergy|allergic", "a": "Allergies can cause itching, sneezing, or rashes. Avoid known triggers."},
    {"q": r"rash|skin allergy", "a": "Apply soothing lotion like calamine. Seek medical care if spreading."},
    {"q": r"itching", "a": "Moisturizers or anti-allergic tablets help reduce itching."},
    {"q": r"acne|pimples", "a": "Wash your face twice daily and avoid oily products."},
    {"q": r"dark circles", "a": "Sleep well and stay hydrated to reduce dark circles."},
    {"q": r"hair fall", "a": "Protein-rich diet and oil massage may help control hair fall."},
    {"q": r"dandruff", "a": "Use anti-dandruff shampoo twice a week."},
    {"q": r"eye pain|eye strain", "a": "Reduce screen time and blink often. Use lubricating drops if needed."},
    {"q": r"red eyes|eye redness", "a": "Avoid rubbing your eyes. Use cold compresses."},
    {"q": r"ear pain", "a": "Ear pain may be due to infection. Keep ears dry."},
    {"q": r"back pain", "a": "Stretching, hot packs, and proper posture help ease back pain."},
    {"q": r"neck pain", "a": "Gentle stretches and warm compresses can relieve neck pain."},
    {"q": r"joint pain|knee pain", "a": "Rest and warm compresses help. Avoid heavy exercise."},
    {"q": r"fatigue|tired|weakness", "a": "Fatigue often results from lack of sleep or nutrition."},
    {"q": r"dehydration", "a": "Drink ORS or electrolyte-rich fluids."},
    {"q": r"bp|blood pressure", "a": "Monitor regularly. Avoid high salt foods."},
    {"q": r"hypertension|high bp", "a": "Reduce salt and manage stress. Consult a doctor for medication."},
    {"q": r"low bp|hypotension", "a": "Drink salty fluids and rest."},
    {"q": r"diabetes", "a": "Manage with diet control, medications, and exercise."},
    {"q": r"high sugar|glucose", "a": "Avoid sweets and monitor levels frequently."},
    {"q": r"cholesterol", "a": "Avoid fried foods and consume more fruits and vegetables."},
    {"q": r"obesity|overweight", "a": "Balanced diet and regular exercise are key."},
    {"q": r"weight loss", "a": "Eat high-fiber foods and reduce junk food intake."},
    {"q": r"weight gain", "a": "Increase protein intake and maintain regular meals."},
    {"q": r"insomnia|can't sleep", "a": "Avoid screens before bed and follow sleep hygiene."},
    {"q": r"stress|anxiety", "a": "Breathing exercises and meditation help reduce anxiety."},
    {"q": r"depression", "a": "Talk to someone you trust. Professional support may be required."},
    {"q": r"panic attack", "a": "Try deep breathing and grounding techniques."},
    {"q": r"burn|burn injury", "a": "Wash with cool water and avoid applying toothpaste."},
    {"q": r"cut|wound", "a": "Clean with antiseptic and keep the wound covered."},
    {"q": r"nosebleed", "a": "Lean forward slightly and pinch the nose for 10 minutes."},
    {"q": r"asthma", "a": "Use prescribed inhalers and avoid dust or smoke."},
    {"q": r"pneumonia", "a": "Seek medical care. Symptoms include fever, chills, and cough."},
    {"q": r"tb|tuberculosis", "a": "TB affects the lungs and requires long-term treatment."},
    {"q": r"heart attack|chest pain", "a": "Chest pain is serious. Seek urgent medical care."},
    {"q": r"stroke", "a": "Immediate medical attention is required."},
    {"q": r"anemia", "a": "Iron-rich foods help such as spinach and beetroot."},
    {"q": r"thyroid", "a": "Monitor TSH levels regularly and follow prescribed medication."},
    {"q": r"hyperthyroid", "a": "Weight loss and irritability may occur. Consult an endocrinologist."},
    {"q": r"hypothyroid", "a": "Symptoms include tiredness and weight gain."},
    {"q": r"migraine", "a": "Avoid loud noises and strong smells. Rest is helpful."},
    {"q": r"ulcer", "a": "Avoid spicy foods and take antacids if needed."},
    {"q": r"pcos|pcod", "a": "Hormonal disorder common in women. Exercise and diet help."},
    {"q": r"pregnant|pregnancy", "a": "Consult a gynecologist for prenatal care."},
    {"q": r"period pain|menstrual pain", "a": "Warm compress and hydration relieve period cramps."},
    {"q": r"urine infection|uti", "a": "Drink plenty of water and avoid holding urine."},
    {"q": r"depression", "a": "Reach out for support from professionals or loved ones."},
    {"q": r"anxiety", "a": "Try breathing exercises and mindfulness."},
    {"q": r"cancer", "a": "Cancer requires specialized medical treatment."},
    {"q": r"jaundice", "a": "Liver-related condition causing yellow skin. Hydration is vital."},
    {"q": r"hepatitis", "a": "Liver inflammation often due to infection."},
    {"q": r"malaria", "a": "Caused by mosquitoes. Fever with chills is common."},
    {"q": r"dengue", "a": "Avoid aspirin. Drink plenty of fluids and monitor platelets."},
    {"q": r"chickenpox", "a": "Common viral infection causing itchy blisters."},
    {"q": r"measles", "a": "Highly contagious disease with fever and rash."},
    {"q": r"autism", "a": "A developmental condition affecting communication."},
    {"q": r"adhd", "a": "Attention disorder common in children."},
    {"q": r"memory loss", "a": "Can be due to stress or aging."},
    {"q": r"vaccination|vaccine", "a": "Vaccines protect against infections."},
    {"q": r"bp medicine", "a": "Only take BP medicines prescribed by a doctor."},
    {"q": r"paracetamol", "a": "Used for fever and mild pain. Follow dosage properly."},
    {"q": r"ibuprofen", "a": "Pain reliever and anti-inflammatory. Avoid on empty stomach."},
    {"q": r"antibiotic", "a": "Use only when prescribed. Don't self-medicate."},
    {"q": r"ointment", "a": "Ointments help heal wounds and rashes."},
    {"q": r"ors", "a": "ORS prevents dehydration. Drink small sips regularly."},
    {"q": r"glucose", "a": "Can boost energy during dehydration."},
    {"q": r"vitamin d", "a": "Sunlight exposure helps improve Vitamin D levels."},
    {"q": r"vitamin c", "a": "Good for immunity. Citrus fruits are rich sources."},
    {"q": r"multivitamin", "a": "Useful for general weakness."},
    {"q": r"exercise", "a": "Regular exercise improves overall health."},
    {"q": r"yoga", "a": "Yoga helps reduce stress and improve flexibility."},
    {"q": r"meditation", "a": "Helps mental calmness and focus."},
    {"q": r"water intake", "a": "Drink 2-3 liters of water daily."},
    {"q": r"healthy diet", "a": "Include proteins, fruits, and vegetables."},
    {"q": r"junk food", "a": "Avoid frequent junk food consumption."},
    {"q": r"smoking", "a": "Smoking harms nearly every organ. Quitting improves health."},
    {"q": r"alcohol", "a": "Excess drinking harms the liver."},
    {"q": r"sleep", "a": "Adults need 7-8 hours of sleep daily."},
    {"q": r"hydration", "a": "Key to maintaining energy levels."},
    {"q": r"sunburn", "a": "Use aloe vera gel and avoid sun exposure."},
    {"q": r"heat stroke", "a": "Cool the body immediately and hydrate."},
    {"q": r"frostbite", "a": "Caused by extreme cold. Warm slowly."},
    {"q": r"food poisoning", "a": "ORS helps. Avoid milk and heavy meals."},
    {"q": r"indigestion", "a": "Eat smaller meals and avoid oily foods."},
    {"q": r"appendix|appendicitis", "a": "Severe right-side abdominal pain; needs urgent care."},
    {"q": r"seizure|fits", "a": "Lay person on their side; don't put anything in mouth."},
    {"q": r"fracture|broken bone", "a": "Immobilize the injured area and seek urgent care."},
    {"q": r"sprain", "a": "Use R.I.C.E — Rest, Ice, Compression, Elevation."},
    {"q": r"tetanus", "a": "Tetanus vaccine is required for deep cuts."},
    {"q": r"infection", "a": "Fever, redness, or swelling indicate infection."},
    {"q": r"immune system", "a": "Healthy diet and sleep boost immunity."},
    {"q": r"liver", "a": "Avoid alcohol and junk to protect liver health."},
    {"q": r"kidney", "a": "Drink enough water to support kidney function."},
    {"q": r"gallbladder", "a": "Gallstones need medical evaluation."},
    {"q": r"appendix", "a": "Sudden right-side pain requires urgent care."},
    {"q": r"eye infection", "a": "Avoid touching eyes and use prescribed drops."},
    {"q": r"skin infection", "a": "Keep area clean and dry."},
    {"q": r"viral", "a": "Viral infections usually need rest and hydration."},
    {"q": r"bacterial", "a": "Bacterial infections require antibiotics."},
    {"q": r"fungal", "a": "Antifungal creams help treat fungal infections."},
    {"q": r"mosquito bite", "a": "Apply ice and avoid scratching."},
    {"q": r"bee sting", "a": "Remove the stinger and apply ice."},
    {"q": r"snake bite", "a": "Seek emergency care immediately."},
    {"q": r"dog bite", "a": "Wash with soap and seek rabies vaccination."},
    {"q": r"rabies", "a": "Rabies is fatal; immediate vaccination is needed."},
    {"q": r"health tips", "a": "Eat healthy, sleep well, and stay hydrated."},
    {"q": r"medicine", "a": "Please specify the medicine name for details."},
    {"q": r"appointment|book|consult", "a": "You can book an appointment on the 'Book Appointment' page."},
    {"q": r"hi|hello|hey", "a": "Hello! How can I assist you today?"},
    {"q": r"thank|thanks", "a": "You're welcome! Stay healthy."},
    {"q": r"bye|goodbye", "a": "Take care! Feel free to ask again."},

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
    {"title": "Asthma", "summary": "Chronic condition causing breathing difficulty.", 
     "detail": "Inflammation narrows airways. Inhalers help manage symptoms."},

    {"title": "Allergies", "summary": "Body overreacts to harmless substances.", 
     "detail": "Caused by pollen, dust, food. Antihistamines reduce symptoms."},

    {"title": "Migraine", "summary": "Severe recurring headache with nausea.", 
     "detail": "Triggers include stress, lights, foods. Painkillers and rest help."},

    {"title": "Tuberculosis", "summary": "Bacterial infection affecting lungs.", 
     "detail": "Treatable with long-term antibiotics."},

    {"title": "Pneumonia", "summary": "Infection causing inflamed lungs.", 
     "detail": "Requires rest, antibiotics, and hydration."},

    {"title": "Bronchitis", "summary": "Inflammation of bronchial tubes.", 
     "detail": "Causes coughing and mucus. Avoid smoke and cold air."},

    {"title": "Sinusitis", "summary": "Inflamed sinuses causing facial pain.", 
     "detail": "Steam inhalation and saline sprays help."},

    {"title": "Arthritis", "summary": "Joint inflammation causing pain.", 
     "detail": "Medication and exercise reduce stiffness."},

    {"title": "Osteoporosis", "summary": "Weak bones prone to fracture.", 
     "detail": "Calcium, vitamin D, and exercise improve bone health."},

    {"title": "Anemia", "summary": "Low red blood cells causing fatigue.", 
     "detail": "Iron-rich foods and supplements help recovery."},

    {"title": "Thyroid Disorder", "summary": "Imbalance in thyroid hormone levels.", 
     "detail": "Hyperthyroidism increases activity; hypothyroidism slows metabolism."},

    {"title": "Jaundice", "summary": "Yellowing of skin due to liver issues.", 
     "detail": "Treat underlying liver condition and stay hydrated."},

    {"title": "Hepatitis A", "summary": "Liver infection from contaminated food/water.", 
     "detail": "Prevention through hygiene and vaccination."},

    {"title": "Hepatitis B", "summary": "Viral liver infection transmitted via fluids.", 
     "detail": "Antiviral therapy and regular monitoring are needed."},

    {"title": "Kidney Stones", "summary": "Hard deposits causing severe pain.", 
     "detail": "Drink plenty of water; may require medical removal."},

    {"title": "Urinary Tract Infection", "summary": "Bacterial infection in urinary system.", 
     "detail": "Burning sensation; treated with antibiotics."},

    {"title": "PCOS", "summary": "Hormonal imbalance in women.", 
     "detail": "Causes irregular periods, weight gain. Requires lifestyle change."},

    {"title": "Heart Attack", "summary": "Blocked blood flow to the heart.", 
     "detail": "Immediate medical attention is required."},

    {"title": "Stroke", "summary": "Interrupted blood supply to the brain.", 
     "detail": "FAST response is important — speech, weakness, confusion."},

    {"title": "Hypertension", "summary": "High blood pressure damaging organs.", 
     "detail": "Exercise, diet control, and regular monitoring are essential."},

    {"title": "Hypotension", "summary": "Low blood pressure causing dizziness.", 
     "detail": "Increase salt intake and stay hydrated."},

    {"title": "Obesity", "summary": "Excess body fat affecting health.", 
     "detail": "Diet, exercise, and lifestyle changes are key."},

    {"title": "Acne", "summary": "Skin condition causing pimples.", 
     "detail": "Clean skin routine and medication help."},

    {"title": "Eczema", "summary": "Dry itchy skin inflammation.", 
     "detail": "Moisturizing and avoiding irritants help."},

    {"title": "Psoriasis", "summary": "Skin cells build up causing patches.", 
     "detail": "Requires topical treatments or phototherapy."},

    {"title": "Dengue Fever", "summary": "Mosquito-borne viral fever.", 
     "detail": "Fever, pain, low platelets; hydration is vital."},

    {"title": "Typhoid", "summary": "Bacterial fever from contaminated water.", 
     "detail": "Treated with antibiotics and fluids."},

    {"title": "Cholera", "summary": "Severe diarrhea from contaminated water.", 
     "detail": "ORS and hydration prevent dehydration."},

    {"title": "Measles", "summary": "Contagious viral infection.", 
     "detail": "Vaccination prevents it. Causes fever and rash."},

    {"title": "Chickenpox", "summary": "Itchy rashes and fever.", 
     "detail": "Rest and calamine lotion help."},

    {"title": "Malaria", "summary": "Mosquito-borne parasite infection.", 
     "detail": "Causes fever and chills; requires antimalarial drugs."},

    {"title": "COVID-19", "summary": "Respiratory illness caused by coronavirus.", 
     "detail": "Causes cough, fever; masks and vaccination help."},

    {"title": "Anxiety", "summary": "Mental health condition causing worry.", 
     "detail": "Deep breathing, therapy, and lifestyle changes help."},

    {"title": "Depression", "summary": "Persistent sadness affecting life.", 
     "detail": "Therapy and medication are effective."},

    {"title": "Insomnia", "summary": "Difficulty falling asleep.", 
     "detail": "Sleep routine and relaxation help."},

    {"title": "Appendicitis", "summary": "Inflamed appendix causing severe pain.", 
     "detail": "Requires immediate surgical removal."},

    {"title": "Gastritis", "summary": "Inflamed stomach lining.", 
     "detail": "Avoid spicy foods; antacids help."},

    {"title": "GERD", "summary": "Acid reflux causing burning sensation.", 
     "detail": "Lifestyle changes and antacids relieve it."},

    {"title": "Diarrhea", "summary": "Frequent loose stools.", 
     "detail": "ORS and hydration prevent dehydration."},

    {"title": "Constipation", "summary": "Difficulty passing stools.", 
     "detail": "Fiber-rich diet and water help."},

    {"title": "Dehydration", "summary": "Lack of body fluids.", 
     "detail": "Drink water, ORS, and avoid heat exposure."},

    {"title": "Epilepsy", "summary": "Neurological disorder causing seizures.", 
     "detail": "Requires anticonvulsant medication."},

    {"title": "Cataract", "summary": "Clouding of the eye lens.", 
     "detail": "Surgery restores clear vision."},

    {"title": "Glaucoma", "summary": "Increased eye pressure leading to vision loss.", 
     "detail": "Eye drops and surgery help control pressure."},

    {"title": "Conjunctivitis", "summary": "Eye infection causing redness.", 
     "detail": "Avoid touching eyes; antibiotic drops help."},

    {"title": "Food Poisoning", "summary": "Illness from contaminated food.", 
     "detail": "Rest, hydration, and bland diet help."},

    {"title": "Heat Stroke", "summary": "Overheating causing collapse.", 
     "detail": "Immediate cooling and hydration needed."},

    {"title": "Sprain", "summary": "Injury to ligaments.", 
     "detail": "RICE therapy — Rest, Ice, Compression, Elevation."}
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

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        name = request.form.get("name")
        amount = request.form.get("amount")
        
        # Fake payment processing
        return render_template("payment_success.html", name=name, amount=amount)
    
    return render_template("payment.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
