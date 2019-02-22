FROM python:3.7-alpine
WORKDIR /var/app
RUN pip install pipenv
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev
COPY ./Pipfile ./Pipfile.lock ./
RUN pipenv install --system
COPY . .
ENTRYPOINT ["python", "app.py"]
