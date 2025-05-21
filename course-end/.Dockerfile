FROM ubuntu:25.04 as ubuntu
RUN apt update
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
COPY . .
RUN yes | apt install python3
RUN yes | apt install python3-tk
RUN yes | apt install python3-libtorrent
CMD ["python3","courseGUI.py"]
# этот Dockerfile был создан для того, чтобы ХОТЯ БЫ собрать вариант без графической оболочки
# ну или с ошибкой от отсутствия переменной окружения DISPLAY