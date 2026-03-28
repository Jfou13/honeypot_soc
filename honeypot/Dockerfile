# base Python light
FROM python:3.9-slim

# Installation des dépendances système Debian
RUN apt-get update && apt-get install -y \
    libmaxminddb0 \
    libmaxminddb-dev \
    mmdb-bin \
    gcc \
	wget \
    && rm -rf /var/lib/apt/lists/*

# Installation manuelle de geoipupdate
RUN wget https://github.com/maxmind/geoipupdate/releases/download/v7.0.1/geoipupdate_7.0.1_linux_amd64.deb \
    && dpkg -i geoipupdate_7.0.1_linux_amd64.deb \
    && rm geoipupdate_7.0.1_linux_amd64.deb

# install libs Python
RUN pip install paramiko mysql-connector-python geoip2 requests

# copie du script dans le conteneur
WORKDIR /app
COPY honeypot.py .

# expose port
EXPOSE 22

# On lance le script
CMD ["python", "honeypot.py"]
