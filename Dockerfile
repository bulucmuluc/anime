FROM python:latest

RUN apt update && apt upgrade -y
RUN apt install python3-pip aria2 ffmpeg -y

RUN cd /
RUN git clone https://github.com/bulucmuluc/anime.git

RUN cd /anime
WORKDIR /anime

RUN pip3 install -U pip
RUN pip3 install -U -r requirements.txt

CMD python3 bot.py
