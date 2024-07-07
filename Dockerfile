FROM python:3.11

RUN apt-get update && apt-get install -y libpq-dev gcc

RUN pip install psycopg2
RUN pip install pyTelegramBotAPI

COPY . /app
WORKDIR app

ENV DATABASE_URL=postgresql://postgres:postgres@host.docker.internal/HHBot
ENV TELEGRAM_TOKEN=7076611927:AAF140f7l3U-zMQT4KACE7aq9iZQli1x3iU

CMD ["python", "app/main.py"]
