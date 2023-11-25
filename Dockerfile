FROM python:3.11-slim-buster
WORKDIR /Investing-Telegram-Bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src src
RUN export PATH="$PATH:/src"; echo $PATH
CMD ["python3", "-O", "src/main.py"]