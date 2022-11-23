FROM python:3.10
WORKDIR /usr/src/app
RUN pip install aiohttp[speedups] py-cord --no-cache-dir
CMD python -u bot.py