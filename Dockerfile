FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt update && apt install -y git

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD git pull https://$GIT_ACCESS_TOKEN@github.com/Xeno-AI/bot.git && python3 -u bot.py