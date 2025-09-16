

# ** PART 1  : Fetch all cities : "locations"**


"""

!pip install selenium
!pip install webdriver-manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from IPython.display import Image
import json
import os
import time
import geopandas as gpd
import os
import requests
import json
import math
from shapely.geometry import box, Point
import numpy as np



zoom = 19  # רמת זום
pixels= 608

import pandas as pd
# קריאת הקובץ
with open('/content/allpoli.json', 'r', encoding='utf-8') as file:
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

all_nodes = []  # מערך לאחסון כל התוצאות

for entry1 in moaza:
  name=entry1['name']
  namehe=entry1['name:he']
  nodes= Fetchnodesfrommoaz(name,namehe)
  all_nodes.extend(nodes)
  print(f"{namehe}-{len(nodes)}")

df = pd.DataFrame(all_nodes)
df.to_csv("all_nodes.csv", index=False, encoding="utf-8")
#כל הקיבוצים כל המושבים

df1 = pd.DataFrame(city)
# שינוי סדר העמודות
columns_order = ["name:he", "latitude", "longitude", "name"]
df1 = df1[columns_order]
df1.to_csv("cities.csv", index=False, encoding="utf-8-sig")
#כל הערים

df_combined = pd.concat([df1, df], ignore_index=True)
df_combined.to_csv("alllocations.csv", index=False, encoding="utf-8-sig")

def Fetchnodesfrommoaz(Moaza,heMoaza) : #webScrapping
#defineChrom options
  chrome_options = Options()
  chrome_options.add_argument("--headless")  # הרצת דפדפן במצב Headless (בלי ממשק גרפי)
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--remote-debugging-port=9222")
  chrome_options.location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
  driver = webdriver.Chrome(chrome_options)
  # כתובת האתר
  url = "https://overpass-turbo.eu/"
  driver.get(url)
  time.sleep(5)
  clear_script = """
  var editor = document.querySelector('.CodeMirror').CodeMirror;
  editor.setValue("");
  query=""
  """
  driver.execute_script(clear_script)
  #print("Cleared existing script content.")
  if "'" in Moaza:  # אם השם מכיל גרש ':
      print("מכיל גרש")
      # Escape לגרשיים וגרש
      escaped_Moaza_name = Moaza.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
      query = f"[out:json];area['name'=\"{escaped_Moaza_name}\"]->.searchArea;(node['place'~'city|village|town|hamlet'](area.searchArea); relation['admin_level'='8'](area.searchArea););out center;"
  elif '"' in Moaza:  # אם השם מכיל גרשיים ":
      print("מכיל גרשיים")
      # Escape לגרשיים וגרש
      escaped_city_name = Moaza.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
      query = f"[out:json];area['name'='{escaped_Moaza_name}']->.searchArea;(node['place'~'city|village|town|hamlet'](area.searchArea); relation['admin_level'='8'](area.searchArea););out center;"

  else:  # אם אין גרשיים או גרש
      query = f"[out:json];area['name'='{Moaza}']->.searchArea;(node['place'~'city|village|town|hamlet'](area.searchArea); relation['admin_level'='8'](area.searchArea););out center;"

  # Escape ל-query
  escaped_query = query.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

  # יצירת סקריפט JavaScript
  insert_script = f"""
  var editor = document.querySelector('.CodeMirror').CodeMirror;
  editor.setValue("{escaped_query}");
  """

# ביצוע הסקריפט בדפדפן
  driver.execute_script(insert_script)
  body = driver.find_element(By.TAG_NAME, "body")
  body.send_keys(Keys.CONTROL, Keys.RETURN)
  #print("Query executed via keyboard on the page.")
  time.sleep(20)
  result_script = """
  var dataElement = document.querySelector('#data');
  if (dataElement) {
      return dataElement.innerText;
  } else {
      return null;
  }
  """
  result = driver.execute_script(result_script)
  he_nodes=[]
  # בדיקת התוצאה
  if result:
      # מציאת ה-JSON הראשון שמתחיל ומסתיים ב-{ ו-}
      start_index = result.index('{')  # מציאת תחילת JSON
      end_index = result.rindex('}') + 1  # מציאת סיום JSON
      valid_json = result[start_index:end_index]  # שליפת JSON תקין
      data = json.loads(valid_json)
      #print(data)
      # ניתוח ה-JSON
      if "elements" in data and len(data["elements"]) > 0:
          #print("Data exists in 'elements'.")
          for element in data.get('elements', []):
            if element.get('type') == 'node':  # בדיקה שהטיפוס הוא node
              tags = element.get('tags', {})  # קבלת תגיות
              name_he = tags.get('name:he', 'Unknown')  # שם בעברית (אם קיים)
              lat = element.get('lat', 'N/A')  # קו רוחב
              lon = element.get('lon', 'N/A')  # קו אורך

              # הוספת המידע לרשימה
              he_nodes.append({'name:he': name_he, 'lat': lat, 'lon': lon,'belongs' : heMoaza})

      else:
          print("No data found in 'elements'.")

  return he_nodes

"""******************************

# **PART 2 **

*******************************************

WebScrapping : download geojson file for city parmater , and poligon kml .
#each city in folder
"""

API_KEY1 = ""


def FetchTheGeoJsonFile(cityName,latitude,hebrewname) : #webScrapping
#defineChrom options
  chrome_options = Options()
  chrome_options.add_argument("--headless")  # הרצת דפדפן במצב Headless (בלי ממשק גרפי)
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--remote-debugging-port=9222")
  download_dir = f"/content/downloads/{hebrewname}"
  if not os.path.exists(download_dir):
      os.makedirs(download_dir)
  chrome_options.add_experimental_option("prefs", {
      "download.default_directory": download_dir,  # תיקיית ההורדה
      "download.prompt_for_download": False,      # ביטול חלון אישור הורדה
      "safebrowsing.enabled": False                # הפעלת הגנת הורדות
  })
  chrome_options.location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
  driver = webdriver.Chrome(chrome_options)

  # כתובת האתר
  url = "https://overpass-turbo.eu/"
  driver.get(url)
  time.sleep(5)

  # ניקוי תוכן קיים בתיבת הסקריפט
  clear_script = """
  var editor = document.querySelector('.CodeMirror').CodeMirror;
  editor.setValue("");
  query=""
  """
  driver.execute_script(clear_script)
  print("Cleared existing script content.")
  if "'" in cityName:  # אם השם מכיל גרש ':
      print("מכיל גרש")
      # Escape לגרשיים וגרש
      escaped_city_name = cityName.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
      query = f"[out:json];relation['name'=\"{escaped_city_name}\"]['boundary'='administrative'];out body;>;out skel qt;"
  elif '"' in cityName:  # אם השם מכיל גרשיים ":
      print("מכיל גרשיים")
      # Escape לגרשיים וגרש
      escaped_city_name = cityName.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
      query = f"[out:json];relation['name'='{escaped_city_name}']['boundary'='administrative'];out body;>;out skel qt;"
  else:  # אם אין גרשיים או גרש
      escaped_city_name = cityName.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
      query = f"[out:json];relation['name'='{escaped_city_name}']['boundary'='administrative'];out body;>;out skel qt;"

  # Escape ל-query
  escaped_query = query.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

  # יצירת סקריפט JavaScript
  insert_script = f"""
  var editor = document.querySelector('.CodeMirror').CodeMirror;
  editor.setValue("{escaped_query}");
  """

# ביצוע הסקריפט בדפדפן
  driver.execute_script(insert_script)
  print("Inserted query:", query)
  body = driver.find_element(By.TAG_NAME, "body")
  body.send_keys(Keys.CONTROL, Keys.RETURN)
  print("Query executed via keyboard on the page.")
  # המתנה לטעינת התוצאות
  time.sleep(20)
  # שליפת התוצאה מ-#data
  result_script = """
  var dataElement = document.querySelector('#data');
  if (dataElement) {
      return dataElement.innerText;
  } else {
      return null;
  }
  """
  result = driver.execute_script(result_script)

  # בדיקת התוצאה
  if result:
      # מציאת ה-JSON הראשון שמתחיל ומסתיים ב-{ ו-}
      start_index = result.index('{')  # מציאת תחילת JSON
      end_index = result.rindex('}') + 1  # מציאת סיום JSON
      valid_json = result[start_index:end_index]  # שליפת JSON תקין
      data = json.loads(valid_json)
      arr=[]
      # ניתוח ה-JSON

      try:
          if "elements" in data and len(data["elements"]) > 0:
              print("Data exists in 'elements'.")
              try:
                  downloader(driver)
                  file_found = wait_for_geojson_download(download_dir, "export.geojson")
                  if file_found:
                      print("The file is ready for further processing.")
                      driver.quit();
                      try:
                          city_polygon = gpd.read_file(f"{download_dir}/export.geojson")  # GeoJSON file
                          geojson_to_kml(city_polygon, cityName, download_dir, "KMLpoligon")
                          arr = splitCitytoArea(city_polygon, cityName, download_dir, latitude)
                          return arr
                      except Exception as e:
                          print(f"Error processing the GeoJSON file or related operations: {e}")
                  else:
                      print("The file was not downloaded in time.")
              except Exception as e:
                  print(f"Error during downloading or handling the GeoJSON file: {e}")
          else:
              print("No data found in 'elements'.")
      except Exception as e:
          print(f"An unexpected error occurred in the main block: {e}")
  return arr

def downloader(driver):
    try:
        # לחיצה על כפתור Export
        export_button = WebDriverWait(driver, 22).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-ide-handler="click:onExportClick"]'))
        )
        export_button.click()
        print("Clicked on Export button.")

    # ניתוח ה-JSON
      #  driver.save_screenshot("/content/screenshot_step1.png")
        #Image(filename="/content/screenshot_step1.png")
    except Exception as e:
        print("Error clicking on Export button:", e)
        return None  # אם יש בעיה, החזר None

    print("**************")


    try:
        # מציאת האלמנט של הקישור הראשון
        first_link = driver.find_element(By.CSS_SELECTOR, "a.export.button.is-small.is-link.is-outlined")
        title = first_link.get_attribute("title")

        # הדפסת תוכן ה-href של הקישור
        href = first_link.get_attribute("href")
        # לחיצה על הקישור (אם נדרש)
        first_link.click()
        print("Clicked on the first download link.")
    except Exception as e:
        print("Error finding or clicking the download link:", e)

def wait_for_geojson_download(download_dir, file_name, timeout=70):
    file_path = os.path.join(download_dir, file_name)
    start_time = time.time()

    while True:
        # בדוק אם הקובץ קיים
        if os.path.exists(file_path):
          print(f"File {file_name} found in download directory.")
          return True

        # בדוק אם הזמן נגמר
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
          print(f"Timeout: File {file_name} not found within {timeout} seconds.")
          return False

        # המתן חצי שנייה לפני בדיקה נוספת
        time.sleep(2)

import geopandas as gpd

def geojson_to_kml(city_polygon,cityName,download_dir,t):
    # צור שם קובץ KML דינמי
    kml_file = os.path.join(download_dir, f"{t}.kml")

    # שמור את הנתונים בפורמט KML
    city_polygon.to_file(kml_file, driver="KML")
    print(f"KML נשמר בנתיב: {kml_file}")

"""# העלאת קובץ פוליגון עיר והמרה לנקודות"""

def splitCitytoArea(city_polygon, cityname, folderlocation, latitude):
    didntfetchgood = []  # מערך לאיסוף ערים שבהן התהליך נכשל

    try:
        total_area = calculate_city_area(city_polygon)

        # חישוב מרכז הפוליגון
        meters = calculate_distance_Meters(latitude, zoom, pixels)
        grid_gdf = get_grid_points(city_polygon, meters, folderlocation, cityname)  # שמירה בתיקיית העיר

        # בדיקת מספר הנקודות
        unique_points = grid_gdf.drop_duplicates()
        poligon_area = meters * meters
        grids = total_area / poligon_area

        # הדפסת ערכים בפורמט מסודר
        print(f"""
        **** תוצאות חישוב הגריד ****
        - גודל התמונה: {meters:.2f} x {meters:.2f} מטרים
        - שטח כל תמונה בקירוב (פוליגון): {poligon_area:.2f} מטרים רבועים
        - שטח העיר הכולל: {total_area:.2f} מטרים רבועים
        - מספר גרידים תאורטי: {grids:.2f}
        - מספר הנקודות בגריד: {len(grid_gdf)}
        ********************************
        """)

        geojson_to_kml(grid_gdf, cityname, folderlocation, "citypoints")

        # יצירת תיקיית תמונות אם אינה קיימת
        images_folder = os.path.join(folderlocation, "images")
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)

        # הורדת תמונה עבור כל מרכז גריד
        print("הורדת התמונות מתחילה")
        for _, row in grid_gdf.iterrows():
            centroid = row.geometry.centroid
            download_image(centroid.y, centroid.x, zoom, APIKEY, images_folder)

        print(f"The process of {cityname} has finished successfully.")

    except Exception as e:
        # אם יש שגיאה, הוסף את העיר למערך
        print(f"Error processing {cityname}: {str(e)}")
        didntfetchgood.append({"city": cityname, "latitude": latitude})

    return didntfetchgood




def get_grid_points(polygon, meters,folderlocation,cityname):
  # גבולות הפוליגון
  minx, miny, maxx, maxy = polygon.total_bounds

  # גודל גריד (144 מטר ~ 0.001296 מעלות גיאוגרפיות בקירוב)
  grid_size=(0.95*meters)/111320

  # יצירת רשת גריד
  x_coords = np.arange(minx, maxx, grid_size)
  y_coords = np.arange(miny, maxy, grid_size)
  grids = []
  for x in x_coords:
      for y in y_coords:
          grids.append(box(x, y, x + grid_size, y + grid_size))

  # יצירת GeoDataFrame של הגריד
  grid_gdf = gpd.GeoDataFrame({"geometry": grids})
  grid_gdf.set_crs(epsg=4326, inplace=True)
  polygon = polygon[polygon.geom_type.isin(['Polygon', 'MultiPolygon'])]
  # חיתוך הגריד כך שיתאים לפוליגון של העיר
  grid_gdf = gpd.overlay(grid_gdf, polygon , how="intersection")
  geofile = os.path.join(folderlocation, "citypointsgrid.geojson")
  # שמירה לקובץ GeoJSON
  grid_gdf.to_file(geofile, driver="GeoJSON")
  return grid_gdf


def calculate_city_area(gdf):
# המרת מערכת קואורדינטות ל-UTM לחישוב שטח מדויק במטרים
    gdf = gdf.to_crs(epsg=32636)  # לדוגמה: ישראל באזור UTM 36N
    area = gdf.area.sum()  # שטח במטרים רבועים
    return area #מ"ר

# פונקציה לחישוב המרחק בקו הרוחב
def calculate_distance_Meters(lat, zoom, pixels, earth_circumference=40075000):
    meters_per_pixel = earth_circumference * math.cos(math.radians(lat)) / (2**zoom * 256)
    return meters_per_pixel * pixels


# פונקציה להורדת תמונה לכל גריד
def download_image(lat, lon, zoom, api_key,images_folder, size="608x608"):
    url = f"https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": size,
        "maptype": "satellite",
        "key": api_key,
    }

    response = requests.get(url, params=params)
    if response.status_code==200 :
    # יצירת שם קובץ בתוך התיקייה
      filename = os.path.join(images_folder, f"satellite_{lat}_{lon}_z{zoom}.png")
      # שמירת התמונה
      with open(filename, "wb") as file:
          file.write(response.content)
      print(f"Saved: {filename}")
    else :
     print(response.status_code)
     print("cant process the image")


didntfetchgood10_50=[]


for element in city[] :
    name = element.get("name") #for search
    namehe=element.get("name:he")
    lat = element.get("latitude")
    lon = element.get("longitude")


    print(namehe, " ", lat)
    arr = FetchTheGeoJsonFile(name, lat,namehe)
    if len(arr) != 0:
      print(f"{namehe} didnt fetch good and add to array")
      didntfetchgood10_50.append({"city": name, "latitude": lat,"namehe" : namehe})