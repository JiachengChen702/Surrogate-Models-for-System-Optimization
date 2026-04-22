FROM ubuntu:22.04
WORKDIR /app
COPY . .

RUN apt update
RUN apt upgrade -y

RUN apt install git -y
RUN apt install pip -y
RUN alias python=python3
RUN apt install vim -y

RUN pip install -r requirements.txt

