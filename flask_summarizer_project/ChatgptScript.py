import re
import json
from openai import OpenAI

# הגדרת המפתח עבור ה-API
chat_api_key = ''
client = OpenAI(api_key=chat_api_key)

def generate_city_recommendations(city_data: dict) -> dict:
    """
    פונקציה שמשתמשת ב-API של OpenAI כדי לייצר המלצות
    עבור עיר מסוימת על בסיס נתונים.
    """
    
    # בדיקה שנתוני העיר מכילים את כל השדות הנדרשים
    if not all(key in city_data for key in ['name', 'population', 'trees', 'factories', 'aqi']):
        print("⚠️ נתוני העיר אינם מלאים. לא ניתן לייצר המלצות AI.")
        return {
            'city_data': city_data,
            'recommendations': [],
            'message': "נתוני עיר חסרים, לא נוצרו המלצות."
        }

    # יצירת הפרומפט עבור מודל השפה על בסיס נתוני העיר
    prompt = f"""
בהתבסס על נתוני העיר הבאים, ספק 3 עד 4 המלצות מעשיות ויישומיות לשיפור איכות החיים בעיר.
ההמלצות חייבות להיות יצירתיות, ממוקדות ורלוונטיות, ולהתבסס אך ורק על הפרמטרים שסופקו:
- כמות מפעלים
- כמות אוכלוסייה (לא ניתן להקטין אותה, רק להתאים לה פתרונות)
- כמות עצים
- כמות תחנות אוטובוס
- כמות רכבים
- גובה מעל פני הים (נתון קבוע שלא ניתן לשנות)

חשוב: כאשר מתייחסים לנושא של שתילת עצים, יש להדגיש שמדובר בשתילת **עצים בוגרים** לצורך שיפור איכות האוויר בטווח המיידי,
ולא שתילה של עצים צעירים שתשפיע רק בעוד שנים רבות.

בהמלצות יש להתייחס לכך שגובה מעל פני הים והאוכלוסייה הם נתונים קבועים שאינם ניתנים לשינוי ישיר,
ולכן הפתרונות חייבים להיות מותאמים למצב הקיים.


החזר את התשובה בפורמט JSON בלבד, בדיוק במבנה הבא:
{{
  "recommendations": [
    {{ "title": "כותרת המלצה 1", "description": "תיאור מפורט..." }},
    {{ "title": "כותרת המלצה 2", "description": "תיאור מפורט..." }},
    {{ "title": "כותרת המלצה 3", "description": "תיאור מפורט..." }}
  ]
}}

נתוני העיר:
שם: {city_data.get('name')}
עצים: {city_data.get('trees')}
תחנות אוטובוס: {city_data.get('busStations')}
רכבים: {city_data.get('cars')}
"""


    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        # שליפת ההמלצות מתוך התגובה בפורמט JSON
        recommendations = data.get('recommendations', [])

        return {
            'city_data': city_data,
            'recommendations': recommendations,
            'message': 'המלצות AI נוצרו בהצלחה.'
        }

    except Exception as e:
        print(f"⚠️ שגיאה בקריאת API ל-OpenAI: {e}")
        return {
            'city_data': city_data,
            'recommendations': [],
            'message': f"שגיאה בעיבוד AI: {e}. לא נוצרו המלצות."
        }

