FROM python:3.10.12-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "telegram_gpt_bot.py"]
