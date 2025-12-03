from flask import Flask, request, jsonify
import pandas as pd
import sqlite3
import joblib
import model  # Importamos el archivo model.py que acabamos de crear

# --- Configuración ---
app = Flask(__name__)
DB_PATH = model.DB_PATH
TABLE_NAME = model.TABLE_NAME

# --- Carga inicial del modelo ---
# Intentamos cargar el modelo al arrancar la API.
# Si no existe, GLOBAL_MODEL será None y la API avisará al usuario.
print("Iniciando API y cargando modelo...")
GLOBAL_MODEL = model.load_model()

# --- Endpoint 1: Predicción de ventas (POST /predict) ---
@app.route('/predict', methods=['POST'])
def predict():
    # Validar si el modelo está cargado
    if GLOBAL_MODEL is None:
        return jsonify({
            "error": "El modelo no está disponible. Ejecuta primero el endpoint /retrain o el script model.py"
        }), 500

    try:
        # 1. Obtener datos (force=True permite leer JSON aunque no se especifique el Header)
        data = request.get_json(force=True)

        # 2. Validar campos necesarios
        required_features = ["TV", "radio", "newspaper"]
        if not all(feature in data for feature in required_features):
            return jsonify({"error": f"Faltan datos. Se requieren: {required_features}"}), 400

        # 3. Preparar DataFrame para el modelo
        input_data = pd.DataFrame([{
            "TV": float(data["TV"]),
            "radio": float(data["radio"]),
            "newspaper": float(data["newspaper"])
        }])

        # 4. Predecir
        prediction = GLOBAL_MODEL.predict(input_data)[0]

        return jsonify({
            "input": data,
            "prediction_sales": round(prediction, 2)
        })

    except ValueError:
        return jsonify({"error": "Los valores deben ser numéricos."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Endpoint 2: Actualizar BD (POST /add_data) ---
@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        data = request.get_json(force=True)
        
        # Corregido el typo 'requiered_fields' -> 'required_fields'
        required_fields = ['TV', 'radio', 'newspaper', 'sales']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Faltan campos. Se requieren: {required_fields}"}), 400

        # Insertar en SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sql_insert = f"INSERT INTO {TABLE_NAME} (TV, radio, newspaper, sales) VALUES (?, ?, ?, ?)"
        values = (float(data['TV']), float(data['radio']), float(data['newspaper']), float(data['sales']))
        
        cursor.execute(sql_insert, values)
        conn.commit()
        conn.close()

        return jsonify({"message": "Registro agregado exitosamente.", "new_record": data}), 201

    except Exception as e:
        return jsonify({"error": f"Error al escribir en BD: {str(e)}"}), 500


# --- Endpoint 3: Reentrenar Modelo (POST /retrain) ---
@app.route('/retrain', methods=['POST'])
def retrain():
    # Usamos la variable global para actualizar el modelo en memoria sin reiniciar la API
    global GLOBAL_MODEL

    # 1. Llamar a la función de entrenamiento en model.py
    success = model.train_and_save_model(data_path=DB_PATH)

    if success:
        # 2. Recargar el modelo en memoria
        new_model = model.load_model()
        if new_model is not None:
            GLOBAL_MODEL = new_model
            return jsonify({"message": "Modelo reentrenado y actualizado en memoria correctamente."}), 200
        else:
            return jsonify({"error": "Entrenamiento correcto, pero fallo al recargar en memoria."}), 500
    else:
        return jsonify({"error": "Fallo durante el entrenamiento. Revisa los logs del servidor."}), 500


# --- Ejecución ---
if __name__ == '__main__':
    # host='0.0.0.0' hace que la API sea visible en tu red local
    app.run(debug=False, host='0.0.0.0', port=5001)