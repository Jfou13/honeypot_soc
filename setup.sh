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
if [ ! -f .env ]; then
    echo -e "${GREEN}[2/3] Génération du fichier .env...${NC}"
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
    echo -e "${BLUE} -> .env créé (Port Dashboard : 8080)${NC}"
else
    echo -e "${BLUE} -> .env existe déjà, aucune modification effectuée.${NC}"
fi

# 3. Vérification Docker
echo -e "${GREEN}[3/3] Vérification du système...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker non trouvé. Installez-le pour continuer.${NC}"; exit 1; }

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}PRÊT À LANCER !${NC}"
echo -e "Dashboard : ${BLUE}http://$(hostname -I | awk '{print $1}'):8080${NC}"
echo -e "Lancement : ${GREEN}docker compose up -d --build${NC}"
echo -e "${BLUE}========================================${NC}"
