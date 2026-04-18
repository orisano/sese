FROM python:3.14-alpine AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /usr/local/app
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev pcre-dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.14-alpine
RUN apk add --no-cache libffi openssl pcre && \
    addgroup -g 1000 sese && adduser -u 1000 -G sese -D sese
COPY --from=build /usr/local/app /usr/local/app
WORKDIR /usr/local/app
EXPOSE 5000
STOPSIGNAL SIGQUIT
CMD ["/usr/local/app/.venv/bin/uwsgi", "--uid", "sese", "--thunder-lock", "--master", "--enable-threads", "--workers", "1", "--http-socket", ":5000", "--module", "app:app"]
