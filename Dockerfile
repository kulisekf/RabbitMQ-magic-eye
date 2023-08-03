FROM python:3.10.12-slim-bullseye

LABEL maintainer="kulisekf"
LABEL version="0.1.0"

#libglib2.0-0 libgl1 -> prerequisite for cv2
RUN apt-get -y update && apt-get -y install libglib2.0-0 libgl1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ADD ./src .

RUN groupadd -r rabbitUser && useradd -r -g rabbitUser rabbitUser

USER rabbitUser

CMD ["python3","sharpening.py"]
