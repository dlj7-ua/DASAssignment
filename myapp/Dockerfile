FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/* /var/tmp/*

RUN mkdir -p /app/app/schemes

COPY ./app ./app
COPY app.py .

RUN ls -la /app/app/schemes/ && \
    echo "Estructura del proyecto:" && \
    find /app -type d

EXPOSE 5000

CMD ["python", "app.py"]
