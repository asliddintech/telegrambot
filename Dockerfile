FROM python:3.11-slim

WORKDIR /app

# Muhit o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]
