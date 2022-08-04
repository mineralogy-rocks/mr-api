###########
# BUILDER #
###########

ARG PYTHON_VERSION=3.8.3-alpine

FROM python:${PYTHON_VERSION} as python

FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=server
ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR ${APP_HOME}

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev make libevent-dev build-base

# install dependencies
COPY src/requirements/base.txt src/requirements/base.txt
COPY src/requirements/server.txt src/requirements/${BUILD_ENVIRONMENT}.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r src/requirements/${BUILD_ENVIRONMENT}.txt


#########
# FINAL #
#########

# pull official base image
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=server
ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR ${APP_HOME}/src

# create the app user
RUN addgroup --system backend \
    && adduser --system --ingroup backend backend

# install dependencies
RUN apk update && apk add libpq gcc python3-dev musl-dev libffi-dev make libevent-dev build-base

COPY --from=python-build-stage /app/wheels /wheels
COPY --from=python-build-stage /app/src/requirements /requirements
RUN pip install --no-cache /wheels/*

COPY --chown=backend:backend ./compose/production/backend/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=backend:backend ./compose/production/backend/start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh
RUN chmod +x /start.sh

COPY . $APP_HOME

# make backend owner of the WORKDIR directory as well.
RUN chown backend:backend ${APP_HOME}

USER backend

ENTRYPOINT ["/entrypoint.sh"]
