import os
import socket
import paramiko
import mysql.connector
import geoip2.database
import requests
import threading
import logging
import time
from datetime import datetime

# On ne garde que les erreurs critiques pour Paramiko
logging.getLogger("paramiko").setLevel(logging.WARNING)

# 1. FICHIER DE LOG : On change le chemin pour qu'il soit créé 
# automatiquement dans le dossier monté par Docker.
logging.basicConfig(filename='data/honey.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

HOST_KEY = paramiko.RSAKey.generate(2048)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME")
}


def get_geo_info_local(ip):
    db_path = '/var/lib/GeoIP/GeoLite2-City.mmdb'
    try:
        with geoip2.database.Reader(db_path) as reader:
            response = reader.city(ip)
            city = response.city.name if response.city.name else ""
            country = response.country.name if response.country.name else "Inconnu"
            lat = response.location.latitude if response.location.latitude else 0
            lon = response.location.longitude if response.location.longitude else 0
            return country, city, lat, lon
    except Exception as e:
        # En cas d'erreur (IP locale, base absente, etc.)
        return "", "Inconnu", 0, 0

def save_to_db(ip, user, pwd):
    # On récupère 4 valeurs
    country, city, lat, lon = get_geo_info_local(ip)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # On ajoute lat et lon dans les colonnes et les %s
        query = """
            INSERT INTO attempts (ip, country, city, lat, lon, username, password, timestamp) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (ip, country, city, lat, lon, user, pwd, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] Erreur insertion MySQL : {e}")

class HoneypotServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        log_msg = f"IP: {self.client_ip} | User: {username} | Pass: {password}"
        print(f"[!] Tentative détectée : {log_msg}")
        
        # 2. LOG DANS LE FICHIER
        logging.info(log_msg)

        # 3. SAUVEGARDE EN BDD
        save_to_db(self.client_ip, username, password)

        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

def handle_connection(client_socket, client_addr):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)
    server = HoneypotServer(client_addr[0])
    try:
        transport.start_server(server=server)
        # On attend que l'attaquant essaie de se connecter (pendant 30 secondes max)
        # Cela laisse le temps à 'check_auth_password' d'être appelé
        channel = transport.accept(30)
        if channel:
            channel.close()
    except Exception as e:
        # On ignore les erreurs de protocole courantes lors des scans
        pass
    finally:
        transport.close()

def start_honeypot():
    port = int(os.environ.get('LISTEN_PORT', 22))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(100)

    # Note : Ajout du 'f' devant le string pour que {port} s'affiche
    print(f"[*] Honeypot SSH lancé sur le port {port}...")

    while True:
        client_socket, client_addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection, args=(client_socket, client_addr))
        thread.start()

def init_db():
    print("[*] Tentative de connexion à MySQL...")
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(45),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    lat FLOAT,
                    lon FLOAT,
                    username VARCHAR(255),
                    password VARCHAR(255),
                    timestamp DATETIME
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("[+] Base de données connectée et table 'attempts' vérifiée.")
            break
        except Exception as e:
            print(f"[-] MySQL n'est pas prêt ({e}), on réessaie dans 5s...")
            time.sleep(5)

if __name__ == "__main__":
# S'assurer que le dossier data existe pour éviter le crash du log
    if not os.path.exists('data'):
        os.makedirs('data')

    init_db()
    start_honeypot()
