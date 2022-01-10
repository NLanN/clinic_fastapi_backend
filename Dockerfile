FROM python:3.8.10-slim-buster as intermediate

RUN apt-get update && apt-get install -y \
    python3-pip

RUN mkdir /opt/app
WORKDIR /opt/app

ENV PYTHONPATH /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r test_requirements.txt

COPY ./src /opt/app
COPY ./run.sh /opt/app

RUN chmod +x run.sh


CMD ["./run.sh"]