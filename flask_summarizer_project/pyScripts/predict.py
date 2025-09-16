import json


def predict(name_he: str,
            numberofpop: float,
            num_fact: float,
            trees: float,
            cars_motor: float,
            cars_electric: float,
            city_heights: float) -> str:
    """
    פונקציה שמחזירה תוצאות חיזוי בפורמט JSON
    """
    # כאן בפועל יבוא הקוד שמבצע את החיזוי והחישובים
    result = {
        "ok": True,
        "city_he": name_he,
        "prediction": {
            "target_name": "aqi_pred",
            "value": 58.3
        },
        "summary": {
            "r2": 0.87,
            "rmse": 6.2,
            "mae": 4.9,
            "amount_of_features": 8,
            "confidence_pct": 92.7
        },
        "feature_importance": [
            {"feature": "עצים", "importance_pct": 24.0},
            {"feature": "כלי רכב", "importance_pct": 19.0},
            {"feature": "אוכלוסייה", "importance_pct": 16.0},
            {"feature": "מספר תעשיות", "importance_pct": 13.0},
            {"feature": "תחנות אוטובוס", "importance_pct": 11.0}
        ],
        "input": {
            "שם": name_he,
            "אוכלוסייה": numberofpop,
            "מספר מפעלים": num_fact,
            "עצים": trees,
            "כלי רכב": cars_motor,
            "מכוניות חשמליות": cars_electric,
            "גובה (מ')": city_heights
        }
    }
    return json.dumps(result, ensure_ascii=False)


# דוגמת שימוש
print(predict("תל אביב", 460000, 120, 150000, 300000, 25000, 40))
