FROM python:3.11-slim
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000

# Konfigurasi Gunicorn untuk Production:
# --workers=4 (Skala standar 2-4 worker per core)
# --threads=2 (Menangani konkurensi request tinggi)
# --worker-class=gthread (Kompatibel dengan logging thread internal aplikasi)
# --timeout=60 (Mencegah blocking dari kalkulasi ML Isolation Forest)
# Logging diarahkan ke stdout/stderr kontainer agar dapat diagregasi log management (Prometheus/Grafana)
CMD ["gunicorn", \
     "--workers=4", \
     "--threads=2", \
     "--worker-class=gthread", \
     "--bind=0.0.0.0:5000", \
     "--timeout=60", \
     "--access-logfile=-", \
     "--error-logfile=-", \
     "app:app"]
