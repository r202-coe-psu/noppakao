FROM debian:sid

RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list

RUN apt update --fix-missing && apt dist-upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales
RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales uwsgi nodejs

ENV LANG th_TH.UTF-8 
ENV LANGUAGE th_TH:en 

RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn uwsgi

WORKDIR /app
COPY noppakao/cmd /app/noppakao/cmd
COPY poetry.lock pyproject.toml /app/

RUN $PYTHON -m pip install --upgrade poetry

RUN $PYTHON -m poetry config virtualenvs.create false 
RUN . /venv/bin/activate && $PYTHON -m poetry install --no-interaction --only main

COPY noppakao/web/static/package.json noppakao/web/static/package-lock.json noppakao/web/static/
RUN npm install --prefix noppakao/web/static
COPY . /app
ENV NOPPHAKAO_SETTINGS=/app/noppakao-development.cfg
