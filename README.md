# sese
sese is moto-server based extended ses mock.

## How to use
### Server
```bash
docker pull orisano/sese
docker run --init -p 5000:5000 orisano/sese
```

or
```bash
git clone --depth=1 https://github.com/orisano/sese
cd sese
docker build -t sese .
docker run --init -p 5000:5000 sese
```

### Client
```bash
# pip install awscli
# aws configure
aws --endpoint-url http://localhost:5000 ses verify-domain-identity --domain example.com
aws --endpoint-url http://localhost:5000 ses send-email --from me@example.com --to to@example.com --subject Test --text Hello
curl http://localhost:5000/message/to@example.com
```
```json
[
  {
    "body": "Hello",
    "source": "me@example.com",
    "subject": "Test"
  }
]
```

## Author
Nao Yonashiro (@orisano)

## License
MIT
