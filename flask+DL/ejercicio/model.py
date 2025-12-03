import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import sqlite3
import os

# --- Configuración ---
# Usamos nombres en minúscula para evitar conflictos en Windows/Linux
MODEL_PATH = r"C:\Users\joseb\Documents\the_bridge\ONLINE_DS_THEBRIDGE_jbenegasb\modulo_1\2509_dsft_thebridge\5-Productivizacion\1-Flask\1-Routing\ejercicios\ejercicio 2 Flask_API_retrain_db\ejercicio\advertising.model"
DB_PATH = r"C:\Users\joseb\Documents\the_bridge\ONLINE_DS_THEBRIDGE_jbenegasb\modulo_1\2509_dsft_thebridge\5-Productivizacion\1-Flask\1-Routing\ejercicios\ejercicio 2 Flask_API_retrain_db\ejercicio\advertising.db"
TABLE_NAME = "sales_data"

def train_and_save_model(data_path=DB_PATH):
    """
    Carga los datos de la DB, entrena un nuevo modelo de regresión lineal 
    y lo guarda en 'advertising.model'.
    """
    try:
        # 1. Conectar a SQLite
        if not os.path.exists(data_path):
            print(f"Error: La base de datos {data_path} no existe.")
            return False

        conn = sqlite3.connect(data_path)
        # Leemos los datos
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        conn.close()

        if df.empty:
            print("La base de datos está vacía.")
            return False

        # 2. Preparación de datos (features: TV, radio, newspaper; target: sales)
        # Aseguramos que solo usamos las columnas correctas
        X = df[["TV", "radio", "newspaper"]]
        y = df["sales"]

        # 3. Entrenar el modelo
        model = LinearRegression()
        model.fit(X, y)

        # 4. Guardar el modelo entrenado
        joblib.dump(model, MODEL_PATH)
        print(f"✅ Modelo reentrenado y guardado exitosamente en: {MODEL_PATH}")
        return True

    except Exception as e:
        print(f"❌ Error al reentrenar/guardar el modelo: {e}")
        return False

def load_model():
    """Carga el modelo de regresión lineal guardado en disco."""
    try:
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ Aviso: No se encontró {MODEL_PATH}. Se debe entrenar primero.")
            return None
            
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        print(f"❌ Error al cargar el modelo: {e}")
        return None

# Bloque para ejecución manual (python model.py)
if __name__ == '__main__':
    print("--- Ejecución manual del script de modelo ---")
    train_and_save_model()