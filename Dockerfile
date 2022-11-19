FROM python:3.11-alpine
WORKDIR /usr/src/app
COPY . .
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install websocket-client requests --no-cache-dir
CMD python -u bot.py