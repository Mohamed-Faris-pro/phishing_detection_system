FROM python:3.12-slim

# Empêche Python d'écrire des fichiers .pyc et force la sortie standard
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installer les dépendances système nécessaires pour PostgreSQL et le ML
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
