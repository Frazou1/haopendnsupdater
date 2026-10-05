FROM python:3.12-slim

# Dépendances Python / Python dependencies
RUN pip install --no-cache-dir requests paho-mqtt==1.6.1

COPY script.py /script.py

# -u : journaux non mis en tampon / unbuffered logs
CMD [ "python3", "-u", "/script.py" ]
