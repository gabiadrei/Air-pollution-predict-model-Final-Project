


#from IPython.display import Image
from PIL import Image
import json
import os
import pandas as pd
import numpy as np
from deepforest import main


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
zoom = 19  # רמת זום
pixels= 608


# קריאת הקובץ
with open('allpoli.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# רשימות למועצות אזוריות וערים
moaza = []
city = []

# מעבר על relations וסיווג לפי שם
for element in data.get('elements', []):
    if element.get('type') == 'relation':
        center = element.get('center', {})
        tags = element.get('tags', {})
        name = tags.get('name', 'Unknown')
        nameHE = tags.get('name:he', 'Unknown')
        lat = center.get('lat', 'N/A')
        lon = center.get('lon', 'N/A')
        entry = {'name': name, 'latitude': lat, 'longitude': lon,'name:he' :nameHE}

        if 'מועצה אזורית' in nameHE:
            moaza.append(entry)
        else:
            city.append(entry)

# הדפסת תוצאות
print(f"Regional Councils (moaza): {len(moaza)}")




def count_trees_in_city(i,city_path, model):
    images_path = os.path.join(city_path, "images")
    total_trees = 0

    if not os.path.exists(images_path):
        return -1
    i=1 
    
    image_files = [f for f in os.listdir(images_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"🖼️ מספר התמונות בתיקייה {images_path}: {len(image_files)}")
    
    for filename in image_files:
       
        image_path = os.path.join(images_path, filename)
        trees_in_image = count_trees_in_image(image_path, model)
        total_trees = total_trees + trees_in_image
        print(f"image {i} / {len(image_files)} - {trees_in_image}  , MOAZA {i}")
        i=i+1
    return total_trees

#notInUse
def count_trees_in_image_with_cropNscale(image_path, model, scale_factor=2, tile_size=400):
    print(f"📸 מפעיל חיתוך לתמונה: {image_path}")

    total_trees = 0

    try:
        img = Image.open(image_path)
        img = img.resize((img.width * scale_factor, img.height * scale_factor), Image.BICUBIC)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        for top in range(0, img.height, tile_size):
            for left in range(0, img.width, tile_size):
                right = min(left + tile_size, img.width)
                bottom = min(top + tile_size, img.height)
                if right - left < tile_size or bottom - top < tile_size:
                    continue
                tile = img.crop((left, top, right, bottom))
                #tile_array = np.array(tile).astype("float32") / 255
                preds = model.predict_image(image=np.array(tile), return_plot=False)
                total_trees += len(preds)
                
    except Exception as e:
        print(f"שגיאה בתמונה {image_path}: {e}")

    return total_trees

def count_trees_in_image(image_path, model) :
    count_df = model.predict_image(path=image_path, return_plot=False)
    if count_df is None:
        #print(f"⚠️ מודל החזיר None עבור {image_path}")
        return 0
    return len(count_df)

def getCitytoArea(i,cityName, latitude, hebrewname,model):
    try:
        total_trees = count_trees_in_city(i,hebrewname, model)
        
        
        return {
            "Moaza" : hebrewname,
             "Total_Trees": total_trees
        }
    except Exception as e:
        print(f"שגיאה בחישוב לעיר {cityName}: {e}")



# טען את המודל
results = [] # שליחת בקשה ושמירת קובץ עבור כל עיר

def runMOAZA():
    print("Strating..............................................")
    results = []
    # טען את המודל פעם אחת
    model = main.deepforest()
    model.use_release()
    
    for i, element in enumerate(moaza[30:], start=1):  # תוכל לשנות את הטווח לכל הרשימה
        name = element.get("name")
        namehe = element.get("name:he")
        if namehe == "מועצה אזורית בוסתן-אל-מרג'" :
             namehe="מועצה אזורית בוסתן אל מראג"
        lat = element.get("latitude")
       

        try:
            print(f"🔄 מריץ עבור:{i} {namehe} ({lat})")
            result = getCitytoArea(i,name, lat, namehe,model)
            if result:
                print(result)
                results.append(result)

        except Exception as e:
            print(f"❌ שגיאה בעיר {namehe}: {e}")
            continue

    # בניית DataFrame ושמירה
    if results:
        df = pd.DataFrame(results)
        df.to_csv("MOAZA_TREES.csv", index=False, encoding='utf-8-sig')
        print("✅ הקובץ MOAZA_TREES.csv נשמר בהצלחה")
    else:
        print("⚠️ לא נשמרו תוצאות – כל הערים נכשלו או ריקות.")
            
#runMOAZA()

