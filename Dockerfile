#	Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START docker]

# The Google App Engine python runtime is Debian Jessie with Python installed
# and various os-level packages to allow installation of popular Python
# libraries. The source is on github at:
# https://github.com/GoogleCloudPlatform/python-docker
FROM python:3.8.3-alpine 
#gcr.io/google_appengine/python

# Create a virtualenv for the application dependencies.
# If you want to use Python 2, use the -p python2.7 flag.
# RUN virtualenv -p python3 /env
# ENV PATH /env/bin:$PATH

# ADD requirements.txt /app/requirements.txt
# RUN /env/bin/pip install --upgrade pip && /env/bin/pip install -r /app/requirements.txt
# ADD . /app

# CMD gunicorn -b :$PORT mrdjango.wsgi
# [END docker]

# set work directory
WORKDIR /usr/src/back-end

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .