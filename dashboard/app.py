import os
from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )


try:
    # On convertit en float direct. Si la variable est vide ou n'est pas un chiffre, 
    # cela lèvera une erreur qui sera capturée par le 'except'.
    SERVER_LAT = float(os.getenv("SERVER_LAT", 0))
    SERVER_LON = float(os.getenv("SERVER_LON", 0))
    
    if SERVER_LAT == 0 and SERVER_LON == 0:
        print("⚠️ WARNING: SERVER_LAT et SERVER_LON sont à 0. Vérifiez votre fichier .env")
except (TypeError, ValueError):
    print("❌ ERREUR: SERVER_LAT ou SERVER_LON invalides dans le .env")
    SERVER_LAT, SERVER_LON = 0, 0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Top 20 Logins
        cursor.execute("SELECT username, COUNT(*) as count FROM attempts GROUP BY username ORDER BY count DESC LIMIT 20")
        logins = cursor.fetchall()
        
        # 2. Top 20 Passwords
        cursor.execute("SELECT password, COUNT(*) as count FROM attempts GROUP BY password ORDER BY count DESC LIMIT 20")
        passwords = cursor.fetchall()

        # 3. Top 10 Couple Login/Password
        cursor.execute("SELECT username, password, COUNT(*) as count FROM attempts GROUP BY username, password ORDER BY count DESC LIMIT 10")
        combos = cursor.fetchall()

        # 4. Top 10 Pays
        cursor.execute("SELECT country, COUNT(*) as count FROM attempts GROUP BY country ORDER BY count DESC LIMIT 10")
        countries = cursor.fetchall()
        
        # 5. 50 dernières tentatives (ID, Coordonnées, et Date)
        cursor.execute("SELECT id, ip, country, city, lat, lon, username, password, timestamp FROM attempts ORDER BY timestamp DESC LIMIT 50")
        recent = cursor.fetchall()

        for attempt in recent:
            if attempt['timestamp']:
                # On ajuste l'heure si le serveur est en UTC (ex: +1h ou +2h pour Paris)
                paris_time = attempt['timestamp'] # + timedelta(hours=1) 
                attempt['timestamp'] = paris_time.strftime('%Y/%m/%d %H:%M:%S')
        
        cursor.close()
        conn.close()

        return jsonify({
            "top_logins": logins,
            "top_passwords": passwords,
            "top_combos": combos,
            "top_countries": countries,
            "recent": recent,
            "server_loc": {
                "lat": SERVER_LAT,
                "lon": SERVER_LON
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE attempts")
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
