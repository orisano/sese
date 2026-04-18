import argparse
import email
import email.parser
import email.policy
import email.header
import os

import flask
import moto.ses
import moto.ses.models
from moto.moto_server.werkzeug_app import create_backend_app

app: flask.Flask = create_backend_app("ses")

DEFAULT_ACCOUNT_ID = "123456789012"
DEFAULT_REGION = "us-east-1"


def _ses_backend():
    return moto.ses.ses_backends[DEFAULT_ACCOUNT_ID][DEFAULT_REGION]


def in_destination(destination, msg):
    if isinstance(msg, moto.ses.models.RawMessage):
        if msg.destinations:
            return destination in msg.destinations
        else:
            message = email.message_from_string(msg.raw_data)
            return any(
                destination in message.get(k, "").split(",")
                for k in ["TO", "CC", "BCC"]
            )

    if isinstance(msg, moto.ses.models.Message):
        return any(destination in v for v in msg.destinations.values())
    return False


def message_to_dict(msg):
    if isinstance(msg, moto.ses.models.RawMessage):
        message = email.parser.Parser(policy=email.policy.default).parsestr(
            msg.raw_data
        )
        return {
            "source": decode_header(message["from"]),
            "subject": decode_header(message["subject"]),
            "body": message.get_body().get_content(),
        }
    if isinstance(msg, moto.ses.models.Message):
        return {"source": msg.source, "subject": msg.subject, "body": msg.body}
    return {}


def decode_header(encoded_header):
    return "".join(
        b if isinstance(b, str) else b.decode(encoding)
        for b, encoding in email.header.decode_header(encoded_header)
    )


@app.route("/message/<destination>", methods=["GET"])
def get_email(destination: str):
    messages = _ses_backend().sent_messages
    return flask.jsonify(
        [message_to_dict(msg) for msg in messages if in_destination(destination, msg)]
    )


_verified_domains = os.getenv("VERIFIED_DOMAINS")
if _verified_domains:
    for domain in _verified_domains.split(","):
        _ses_backend().verify_domain(domain.strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H", "--host", type=str, help="Which host to bind", default="0.0.0.0"
    )
    parser.add_argument(
        "-p", "--port", type=int, help="Port number to use for connection", default=5000
    )
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
