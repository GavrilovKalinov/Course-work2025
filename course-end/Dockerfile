FROM ubuntu:25.04 as ubuntu
RUN apt update
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
COPY courseGUI.py .
COPY coursecore.py .
RUN yes | apt install python3
RUN yes | apt install python3-tk
RUN yes | apt install python3-libtorrent
RUN yes | apt install xauth
CMD ["python3","courseGUI.py"]
