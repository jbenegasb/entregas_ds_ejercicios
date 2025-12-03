import pandas as pd
import sqlite3
import os

# --- Configuración ---
CSV_PATH = r"1-Routing\ejercicios\ejercicio 2 Flask_API_retrain_db\ejercicio\Advertising.csv"
DB_PATH = r"C:\Users\joseb\Documents\the_bridge\ONLINE_DS_THEBRIDGE_jbenegasb\modulo_1\2509_dsft_thebridge\5-Productivizacion\1-Flask\1-Routing\ejercicios\ejercicio 2 Flask_API_retrain_db\ejercicio\advertising.db"
TABLE_NAME = "sales_data"

def initialize_database():
    """
    Lee el archivo CSV, verifica que exista y carga su contenido 
    en una nueva tabla (o sobrescribe la existente) en SQLite.
    """
    print("--- 🚀 Inicializando la base de datos SQLite ---")
    
    # 1. Verificar existencia del CSV
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: No se encontró el archivo CSV en la ruta: {CSV_PATH}")
        return

    try:
        # 2. Leer el CSV y limpiar datos
        df = pd.read_csv(CSV_PATH) 
        
        
        
        # 3. Conectar a SQLite. Si el archivo DB no existe, lo crea.
        conn = sqlite3.connect(DB_PATH)
        
        # 4. Cargar los datos del DataFrame a la tabla SQLite
        # 'if_exists="replace"' borra la tabla si existe y la crea de nuevo.
        # Esto asegura una inicialización limpia.
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"✅ Éxito: Se han cargado {len(df)} registros del CSV a la tabla '{TABLE_NAME}' en {DB_PATH}.")
        
    except Exception as e:
        print(f"❌ Error fatal durante la inicialización de la base de datos: {e}")

if __name__ == '__main__':
    initialize_database()