FROM python:3.9-slim
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir flask flask-sqlalchemy psycopg2-binary redis gunicorn
COPY . .
COPY nginx.conf /etc/nginx/sites-available/default
COPY supervisord.conf /etc/supervisord.conf
RUN mkdir -p /run/app && chown -R www-data:www-data /run/app
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
