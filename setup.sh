#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}==== INSTALLATION HONEYPOT SOC (MODE DIRECT) ====${NC}"

# 1. Création des dossiers nécessaires
echo -e "${GREEN}[1/3] Création des répertoires de données...${NC}"
mkdir -p data/geoip
mkdir -p dashboard/templates
mkdir -p dashboard/static

# 2. Préparation du fichier .env
echo -e "${GREEN}[2/3] Configuration du fichier .env...${NC}"

DB_PASS=""
DB_ROOT=""

if [ ! -f .env ]; then
    DB_PASS=$(openssl rand -hex 12)
    DB_ROOT=$(openssl rand -hex 16)

    cat <<EOF > .env
# Configuration Base de données
DB_NAME=db_honey
DB_USER=admin_honey
DB_PASS=$DB_PASS
DB_ROOT_PASS=$DB_ROOT

# Géolocalisation du serveur
SERVER_LAT=52.3785
SERVER_LON=4.89998

# Ports (Accessibles depuis l'extérieur)
SSH_PORT=22
DASHBOARD_PORT=8080
EOF

    echo -e "${BLUE} -> .env créé.${NC}"
    echo -e "${BLUE} -> DB_PASS: $DB_PASS${NC}"
    echo -e "${BLUE} -> DB_ROOT_PASS: $DB_ROOT${NC}"
elif grep -q '^DB_PASS=<your_db_password_here>' .env || grep -q '^DB_ROOT_PASS=<your_db_root_password_here>' .env; then
    DB_PASS=$(openssl rand -hex 12)
    DB_ROOT=$(openssl rand -hex 16)

    sed -i "s#^DB_PASS=.*#DB_PASS=$DB_PASS#" .env
    sed -i "s#^DB_ROOT_PASS=.*#DB_ROOT_PASS=$DB_ROOT#" .env

    echo -e "${BLUE} -> .env mis à jour avec des mots de passe aléatoires.${NC}"
    echo -e "${BLUE} -> DB_PASS: $DB_PASS${NC}"
    echo -e "${BLUE} -> DB_ROOT_PASS: $DB_ROOT${NC}"
else
    echo -e "${BLUE} -> .env existe déjà et contient des mots de passe valides (pas de modification).${NC}"
fi

SSH_PORT=$(grep '^SSH_PORT=' .env | cut -d'=' -f2)
echo -e "${BLUE} -> SSH_PORT: $SSH_PORT${NC}"

# 3. Vérification Docker
echo -e "${GREEN}[3/3] Vérification du système...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker non trouvé. Installez-le pour continuer.${NC}"; exit 1; }

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}PRÊT À LANCER !${NC}"
echo -e "Dashboard : ${BLUE}http://$(hostname -I | awk '{print $1}'):8080${NC}"
echo -e "Lancement : ${GREEN}docker compose up -d --build${NC}"
echo -e "${BLUE}========================================${NC}"
