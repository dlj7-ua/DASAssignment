# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 1. Copiar solo lo necesario para instalar dependencias
COPY requirements.txt .

# 2. Instalar dependencias con limpieza de caché
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/* /var/tmp/*

# 3. Crear estructura de directorios necesaria
RUN mkdir -p /app/app/schemes

# 4. Copiar el resto de archivos en dos pasos
COPY ./app ./app
COPY app.py .

# 5. Verificar que los esquemas se copiaron (para debug)
RUN ls -la /app/app/schemes/ && \
    echo "Estructura del proyecto:" && \
    find /app -type d

# Exponer el puerto
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
