FROM python:3.10
WORKDIR /usr/src/app
COPY . .
RUN pip install aiohttp[speedups] py-cord psutil --no-cache-dir
CMD python -u bot.py
