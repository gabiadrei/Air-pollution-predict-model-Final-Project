from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import threading
import time
import json
from predict import predict
from ChatgptScript import generate_city_recommendations # ייבוא הפונקציה מהקובץ chatscript.py



app = Flask(__name__)
app.secret_key = "ttttttttttttttttttttttttt"  # חובה בשביל session

USERS = {
    "admin": "admin",
    "gabi": "adrei"
}

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/login')
def login():
    return render_template('login.html')
    
    
@app.route('/main')
def main():
    return render_template('main.html')
    
@app.route('/predict', methods=['GET'])
def show_predict_page():
    return render_template('predict.html')

# נתיב המטפל בביצוע החיזוי (בקשת POST)
@app.route('/predict', methods=['POST'])
def run_prediction():
    try:
        # קבלת נתוני ה-JSON שנשלחו מהלקוח
        data = request.json
        name_he = data.get('name_he')
        numberofpop = data.get('numberofpop')
        num_fact = data.get('num_fact')
        trees = data.get('trees')
        cars_motor = data.get('cars')
        bus = data.get('bus')
        city_heights = data.get('city_heights')

        # קריאה לפונקציית החיזוי שלך
        prediction_result_json = predict(
            name_he,
            numberofpop,
            num_fact,
            trees,
            cars_motor,
            bus,
            city_heights
        )

        # החזרת התוצאה כ-JSON ללקוח
        return prediction_result_json

    except Exception as e:
        # טיפול בשגיאות והחזרת הודעת שגיאה מתאימה
        return jsonify({"ok": False, "error": str(e)}), 500

# נתיב חדש: טיפול בבקשת POST ליצירת המלצות AI
@app.route('/api/generate_recommendations', methods=['POST'])
def handle_ai_recommendations():
    """
    נקודת קצה שמקבלת נתוני עיר מהלקוח, מפעילה את פונקציית ה-AI
    ומחזירה את ההמלצות שנוצרו.
    """
    if not request.is_json:
        return jsonify({"error": "תוכן הבקשה חייב להיות JSON"}), 400
    
    city_data = request.get_json()
    
    # קריאה לפונקציית ה-AI ליצירת המלצות
    response_data = generate_city_recommendations(city_data)
    
    # החזרת ההמלצות ללקוח
    return jsonify(response_data), 200

# נתיב מעודכן: טיפול בבקשת POST שמכילה את הנתונים המלאים
@app.route('/offer', methods=['POST'])
def offer():
    city_data_raw = request.form.get('cityData')
    recommendations_raw = request.form.get('recommendations')

    city_data = json.loads(city_data_raw) if city_data_raw else {}
    recommendations = json.loads(recommendations_raw) if recommendations_raw else []

    return render_template(
        'hamlaza.html',
        city_data=city_data,
        recommendations=recommendations
    )


@app.route('/reports')
def reports():
    return render_template('report.html')
    
##############################33 
    
@app.route('/Confirm', methods=['POST'])
def Confirm():
    # הדפסה גולמית של כל הטופס
    print("RAW FORM:", request.form, flush=True)

    # שליפה בטוחה
    username = request.form.get('username')
    password = request.form.get('password')

    # הדפסה ממוקדת (לא חושף סיסמה, רק אורך)
    print(f"username={username!r}, password_present={password is not None}, password_len={len(password) if password else 0}", flush=True)

    # לוגיקת התחברות כרגיל
    if username in USERS and USERS[username] == password:
        return redirect(url_for('loading'))
    else:
        return render_template('login.html', error="שם משתמש או סיסמה שגויים"), 401


    

@app.route('/loading')
def loading():
    return render_template("loading.html")

@app.route('/status')
def status():
    return jsonify({"status": task["status"]})

@app.route('/result')
def result():
    return render_template(
        "result.html",
        summery=task["summary"],
        query=task["query"],
        start_year=task["start_year"],
        end_year=task["end_year"],
        tags=task["tags"],
        articles=task["articles"]
    )





if __name__ == '__main__':
    app.run(debug=True)