FROM python:3.8-alpine
WORKDIR /usr/local/app
RUN addgroup -g 1000 sese && adduser -u 1000 -G sese -D sese
COPY --chown=sese ./Pipfile ./Pipfile.lock ./
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev pcre-dev && \
    apk add --no-cache --virtual .run-deps musl libffi openssl pcre && \
    pip3 install --no-cache pipenv==2018.11.26 && \
    pipenv install --system --clear --deploy && \
    apk del .build-deps && \
    rm -rf /usr/local/lib/python3.8/config-3.8m-x86_64-linux-gnu && \
    chown -R sese:sese /usr/local/lib/python3.8 && \
    rm -rf /root/.cache
COPY --chown=sese . .
EXPOSE 5000
STOPSIGNAL SIGQUIT
CMD ["uwsgi", "--uid", "sese", "--thunder-lock", "--master", "--enable-threads", "--workers", "1", "--http-socket", ":5000", "--module", "app:app"]
