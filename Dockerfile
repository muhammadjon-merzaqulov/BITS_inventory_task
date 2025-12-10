# ------------------------------
#  Base Python image
# ------------------------------
FROM python:3.12-slim

# ------------------------------
#  Work directory
# ------------------------------
WORKDIR /app

# ------------------------------
#  Python optimization
# ------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ------------------------------
#  Install OS dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
#  Install Python dependencies
# ------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# ------------------------------
#  Copy project
# ------------------------------
COPY . .

# ------------------------------
#  Collect static
# ------------------------------
RUN python manage.py collectstatic --noinput

# ------------------------------
#  Expose port
# ------------------------------
EXPOSE 8000

# ------------------------------
#  Start Gunicorn
# ------------------------------
CMD ["gunicorn", "inventory_system.wsgi:application", "--bind", "0.0.0.0:8000"]
