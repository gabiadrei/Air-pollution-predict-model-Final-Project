import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

def load_fun():
        file_path  = "static/data/newdatajsonfortest.csv"
        df = pd.read_csv(file_path)
        return df


def metrics(y_true, y_pred):
    MAE = mean_absolute_error(y_true, y_pred)
    RMSE=np.sqrt(mean_squared_error(y_true, y_pred))
    Rsquared = r2_score(y_true, y_pred)
    return MAE,RMSE,Rsquared


def scaling(X_train, X_test):
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)
  return X_train_scaled,X_test_scaled

def return_the_testCity(X_test,y_test,city_row_x,city_row_y):
    feature_names = ["aqi_global"]
    
    city_row_x=city_row_x.drop(columns=["hebname"])
   
    feature_names_city = X_test.columns.tolist()
    
    X_test_df=pd.DataFrame(X_test, columns=feature_names_city)
    Y_test_df = pd.DataFrame(y_test, columns=feature_names)  
    city_row_y=city_row_y.to_frame(name="aqi_global")
    
    X_test = pd.concat([X_test_df, city_row_x], axis=0)
    
    y_test = pd.concat([Y_test_df, city_row_y], axis=0)
    
    return X_test,y_test
 
def standertiztion(df):
    
    df["cars_per_person"] = df["cars"] / (df["numberofpop"] ).replace(0, np.nan)* 1000
    df["bus_per_person"] = df["busStations"] / (df["numberofpop"]).replace(0, np.nan)* 1000
    df['numberofpop'] = np.log1p(df['numberofpop'])
    df = df.replace([np.inf, -np.inf], np.nan)   # להחליף אינסוף ב-NaN
    df = df.fillna(df.median(numeric_only=True)) # למלא NaN בחציון של כל עמודה
    return df
 
def drop_not_prametric_data(df):
    df = df.drop(columns=['lat','lan','cars','busStations','pol_fact','amount_of_pol','num_fact','belogns','type'])
    
    return df
    
def preproccess(df):
    """ נרמול ניתונים """
    df=standertiztion(df)     
    """ הפרדת מאפיינים X ועמודת מטרה Y """    
    x=drop_not_prametric_data(df)
    target_column = "aqi_global"
    y = df[target_column]
    x=x.drop(columns=['aqi_global'])
    feature_names=x.columns.tolist()
    
    return x,y,feature_names
    
    
def split(x,y):
    """ חלוקה לפי אימון ובדיקה"""
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    return X_train,X_test,y_train, y_test
    
 
    
def drop_the_test(x,y,city_name_he):
    city_idx = x.index[x["hebname"].astype(str).str.strip().eq(str(city_name_he).strip())].item()  
    city_row_y = y.loc[[city_idx]]      # נשמר כ-DataFrame בגודל 1×p
    city_row_x = x.loc[[city_idx]]  
    x_rest  = x.drop(index=city_idx) # כל הנתונים בלי העיר
    y_rest  = y.drop(index=city_idx)
    x_rest=x_rest.drop(columns=["hebname"])
    city_row_x=city_row_x.drop(columns=["hebname"])
    return city_row_x,city_row_y, x_rest, y_rest ,city_idx


def preparing_city_test(city_name_he,numberofpop,num_fact,trees,cars,bus,city_heights):
  
    newn_row = [{'hebname': city_name_he, 'cars': cars, 'num_fact': num_fact,'trees': trees, 'busStations': bus,
                 'city_heights': city_heights,'numberofpop': numberofpop, 'lat': 111, 'lan': 111,'pol_fact':1,
                 'amount_of_pol':0,'belogns':'f','type':'f'}]
    newn_row_df = pd.DataFrame(newn_row)
    newn_row_df["numberofpop"] = pd.to_numeric(newn_row_df["numberofpop"], errors="coerce")
    newn_row_df["cars"] = pd.to_numeric(newn_row_df["cars"], errors="coerce")
    newn_row_df["busStations"] = pd.to_numeric(newn_row_df["busStations"], errors="coerce")
    newn_row_df["city_heights"] = pd.to_numeric(newn_row_df["city_heights"], errors="coerce")
    newn_row_df["trees"] = pd.to_numeric(newn_row_df["trees"], errors="coerce")
    newn_row_df=standertiztion(newn_row_df)
    newn_row_df=drop_not_prametric_data(newn_row_df)
   
    return newn_row_df

def run_random_forest(X_train, X_test, y_train, y_test,feature_names):
    model = RandomForestRegressor(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
   # names = list(model.feature_names_in_)
  
    feature_names.remove("hebname")
    
    importances_rf = model.feature_importances_
    rf_feature_importance = pd.Series(importances_rf, index=feature_names).sort_values(ascending=True)

    MAE,RMSE,Rsquared=metrics(y_test, y_pred)
    return y_pred,MAE,RMSE,Rsquared,rf_feature_importance


def run_fun(city_name_he,numberofpop,num_fact,trees,cars,bus,city_heights): 
    df=load_fun()
    x,y,feature_names=preproccess(df)
    """ preparing the test city"""
    newn_row_df=preparing_city_test(city_name_he,numberofpop,num_fact,trees,cars,bus,city_heights)
    """ dropping the test city from the database """
    city_row_x,city_row_y,x,y,city_idx=drop_the_test(x,y,city_name_he)
    """spliting to train and test set"""

    X_train,X_test,y_train, y_test=split(x,y)
    """ adding the test city to the test set for predict"""
    X_test,y_test=return_the_testCity(X_test,y_test,newn_row_df,city_row_y)
    X_train,X_test=scaling(X_train,X_test)
    
   
    y_pred,MAE,RMSE,Rsquared,importances_rf=run_random_forest(X_train, X_test, y_train, y_test, feature_names)
    
  
    return y_pred,MAE,RMSE,Rsquared,importances_rf,city_idx,df
    

def predict(name_he: str,
            numberofpop: float,
            num_fact: float,
            trees: float,
            cars: float,
            bus: float,
            city_heights: float)-> str:
           
    """
    פונקציה שמחזירה תוצאות חיזוי בפורמט JSON
    """
    y_pred,MAE,RMSE,Rsquared,importances_rf,city_idx,df=run_fun(name_he,numberofpop,num_fact,trees,cars,bus,city_heights)
    #prec= (y_pred[-1] / df.loc[city_idx, 'aqi_global']) * 100
    prec = (1 - abs(y_pred[-1] - df.loc[city_idx, 'aqi_global']) / df.loc[city_idx, 'aqi_global']) * 100
    
    # כאן בפועל יבוא הקוד שמבצע את החיזוי והחישובים
    result = {
        "ok": True,
        "city_he": name_he,
        "prediction": {
            "target_name": "aqi_pred",
            "value": y_pred[-1]
        },
        "summary": {
            "r2": Rsquared,
            "rmse": RMSE,
            "mae": MAE,
            "amount_of_features": 5,
            "confidence_pct": prec, 

        },
        "feature_importance": [
            {"feature": "עצים", "importance_pct": importances_rf["trees"]*100},
            {"feature": "כלי רכב", "importance_pct": importances_rf["cars_per_person"]*100},
            {"feature": "אוכלוסייה", "importance_pct": importances_rf["numberofpop"]*100},
            #{"feature": "מספר תעשיות", "importance_pct": importances_rf[""]},
            {"feature": "גובה מעל פני הים", "importance_pct": importances_rf["city_heights"]*100},
            {"feature": "תחנות אוטובוס", "importance_pct":importances_rf["bus_per_person"]*100}
        ],
        "input": {
            "שם": name_he,
          "אוכלוסייה": numberofpop,
            "מספר מפעלים": num_fact,
            "עצים": trees,
            "כלי רכב": cars,
            "תחנות אוטובוס": bus,
            "גובה (מ')": city_heights
        }
    }
    return json.dumps(result, ensure_ascii=False)





