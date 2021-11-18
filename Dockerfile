FROM python:3.7.11-buster

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends libsm6 libxext6 \
  libpq-dev --no-install-recommends \
  && apt-get install gcc -y \
  && apt-get clean \
  && apt-get install -y wget \
  && apt-get -y install libgtk2.0-dev

ENV INSTALL_PATH /zombie
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
# RUN pip install --editable .

CMD gunicorn -c python:config.gunicorn zombie.app:app
