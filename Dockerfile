FROM python:3.11-alpine
WORKDIR /usr/src/app
RUN pip install websocket-client requests --no-cache-dir
CMD python -u bot.py