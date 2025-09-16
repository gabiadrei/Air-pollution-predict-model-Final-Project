

import geopandas as gpd
#from IPython.display import Image
from PIL import Image
import json
import os
import pandas as pd
import math
import numpy as np
from deepforest import main
import matplotlib.pyplot as plt
import os
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from shapely.ops import transform
from pyproj import Transformer
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from deepforest import visualize

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
print(f"Cities (city): {len(city)}")

def calculate_kml_area_km2(path_to_kml):
    # טען את קובץ ה-KML
    tree = ET.parse(path_to_kml)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    # חפש את הקואורדינטות של הפוליגון הראשון
    coords_text = root.find(".//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
    if coords_text is None:
        raise ValueError("לא נמצאו קואורדינטות של Polygon בקובץ")

    # פירוק הקואורדינטות
    coord_pairs = coords_text.text.strip().split()
    polygon_points = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in coord_pairs]

    # יצירת פוליגון גיאוגרפי
    polygon = Polygon(polygon_points)

    # המרת הפוליגון למערכת קואורדינטות מטרית (UTM - Israel Zone)
    project = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform
    polygon_meters = transform(project, polygon)

    # חישוב שטח בקמ"ר
    area_sqm = polygon_meters.area
    area_sqkm = area_sqm / 1_000_000
    return area_sqkm


def count_trees_in_city(city_path, model):
    images_path = os.path.join(city_path, "images")
    total_trees = 0

    if not os.path.exists(images_path):
        return 0
    i=1 
    
    image_files = [f for f in os.listdir(images_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"🖼️ מספר התמונות בתיקייה {images_path}: {len(image_files)}")
    
    for filename in image_files:
       
        image_path = os.path.join(images_path, filename)
        trees_in_image = count_trees_in_image(image_path, model)
        total_trees = total_trees + trees_in_image
        print(f"image {i} - {trees_in_image}")
        i=i+1
    return total_trees

#notInUse
def count_trees_in_image_with_cropNscale(image_path, model, scale_factor=2, tile_size=400):
    print(f"📸 מפעיל חיתוך לתמונה: {image_path}")

    total_trees = 0
    tile_index = 0

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
                tile_np = np.array(tile)

                try:
                    # ניבוי: גם תוצאה גרפית וגם DataFrame
                    plot = model.predict_image(image=tile_np, return_plot=True)
                    count_df = model.predict_image(image=tile_np, return_plot=False)
                    total_trees += len(count_df)

                    # הצגת התמונה עם תיבות עבור ה-tile הנוכחי
                    plt.figure(figsize=(8, 8))
                    plt.imshow(plot.astype("uint8"))
                    plt.title(f"Detected Trees - Tile {tile_index}")
                    plt.axis('off')
                    plt.show()
                    plt.close() # סגירת ה-plot כדי לפנות זיכרון

                    print(f"🌳 Tile {tile_index}: {len(count_df)} עצים זוהו")

                except Exception as e_tile:
                    print(f"שגיאה בעיבוד או הצגת Plot עבור חלק {tile_index}: {e_tile}")

                tile_index += 1

    except Exception as e:
        print(f"שגיאה בתמונה {image_path}: {e}")

    return total_trees


def count_trees_in_image(image_path, model) :
    count_df = model.predict_image(path=image_path, return_plot=False)
    if count_df is None:
        #print(f"⚠️ מודל החזיר None עבור {image_path}")
        return -1
    return len(count_df)

def getCitytoArea(cityName, latitude, hebrewname,model):
    try:
        #kml_path = f"{hebrewname}/KMLpoligon.kml"
        #total_area = calculate_kml_area_km2(kml_path)

        # חישוב גודל כל ריבוע (בהנחה שיש לך את הפונקציה)
        #meters = calculate_distance_Meters(latitude, zoom, pixels)

        # טעינת נקודות הגריד
        #geojson_path = f"{hebrewname}/citypointsgrid.geojson"
        #grid_gdf = gpd.read_file(geojson_path)
       # grid_gdf = grid_gdf.to_crs(epsg=4326)

        # בדיקת ייחודיות נקודות
        #unique_points = grid_gdf.drop_duplicates()
       # poligon_area = meters * meters

        
        
        total_trees = count_trees_in_city(hebrewname, model)
        
        
        return {
            "City" : hebrewname,
            #"Area_m2": total_area
            #"Grid_Meters": meters,
          #  "Single_Tile_Area_m2": poligon_area,
          #  "Num_Grid_Points": len(unique_points),
             "Total_Trees": total_trees
        }
    except Exception as e:
        print(f"שגיאה בחישוב לעיר {cityName}: {e}")

def calculate_city_area(gdf):
   try:
        gdf = gdf.to_crs(epsg=32636)
        area = gdf.area.sum()  # שטח כולל במ"ר
        return area
   except Exception as e:
        print(f"שגיאה בחישוב שטח: {e}")
        return 0
      
# פונקציה לחישוב המרחק בקו הרוחב
def calculate_distance_Meters(lat, zoom, pixels, earth_circumference=40075000):
    meters_per_pixel = earth_circumference * math.cos(math.radians(lat)) / (2**zoom * 256)
    return meters_per_pixel * pixels



# טען את המודל
def testmodel_on_folder(folder_path,model):
    # קבל את כל התמונות בתיקייה
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]

    if not image_files:
        print("⚠️ לא נמצאו קבצי PNG בתיקייה")
        return

    for image_name in image_files:
        image_path = os.path.join(folder_path, image_name)
       

        try:
            # ניבוי: גם תוצאה גרפית וגם DataFrame
           plot = model.predict_image(path=image_path, return_plot=True)
           count_df = model.predict_image(path=image_path, return_plot=False)
           other= count_trees_in_image(image_path,model)

            # הצגת התמונה עם תיבות
           plt.figure(figsize=(8, 8))
           plt.imshow(plot.astype("uint8"))
           plt.title(f"Detected Trees - {image_name}")
           plt.axis('off')
           plt.show()

           print(f"🌳 {image_name}: {len(count_df)} עצים זוהו")
           print(f"🌳 {image_name}: {other} other עצים זוהו")

        except Exception as e:
            print(f"❌ שגיאה בהרצת המודל על {image_name}: {e}")
            
#testmodel_on_folder("testimages",model)
#pathe="C:/Users/USER/Desktop/test.png"
#test = count_trees_in_image(pathe,model)
#print(test)
results = [] # שליחת בקשה ושמירת קובץ עבור כל עיר

def runCities():
    print("Strating..............................................")
    results = []
    # טען את המודל פעם אחת
    model = main.deepforest()
    model.use_release()
    
    for i, element in enumerate(city[:], start=1):  # תוכל לשנות את הטווח לכל הרשימה
        name = element.get("name")
        namehe = element.get("name:he")
        lat = element.get("latitude")
       # lon = element.get("longitude")

        try:
            print(f"🔄 מריץ עבור:{i} {namehe} ({lat})")
            result = getCitytoArea(name, lat, namehe,model)
            if result:
                print(result)
                results.append(result)

        except Exception as e:
            print(f"❌ שגיאה בעיר {namehe}: {e}")
            continue

    # בניית DataFrame ושמירה
    if results:
        df = pd.DataFrame(results)
        #df.to_csv("city_grid_summary.csv", index=False, encoding='utf-8-sig')
        df.to_csv("city_area.csv", index=False, encoding='utf-8-sig')
        print("✅ הקובץ city_grid_summary.csv נשמר בהצלחה")
    else:
        print("⚠️ לא נשמרו תוצאות – כל הערים נכשלו או ריקות.")
            
#runCities()

model = main.deepforest()
model.use_release()
#test="C:/Users/USER/Desktop/testimages"
#testmodel_on_folder(test,model)

pa="C://Users/USER/Desktop/testimages/3.png"
if not os.path.isfile(pa):
    print(f"⚠️ קובץ התמונה לא נמצא: {pa}")
else:
    print("✅ הקובץ קיים, ממשיך...")
    total=count_trees_in_image_with_cropNscale(pa,model)
    print(total)