FROM python:3.11
WORKDIR /Investing-Telegram-Bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src src
RUN export PATH="$PATH:/src"; echo $PATH
CMD ["python3", "src/main.py"]