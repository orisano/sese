import argparse
import email
import email.parser
import email.policy
import email.header
import typing

import flask
import moto.server
import moto.ses
import moto.ses.models

app: flask.Flask = moto.server.create_backend_app("ses")


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
    messages = moto.ses.ses_backend.sent_messages
    return flask.jsonify(
        [message_to_dict(msg) for msg in messages if in_destination(destination, msg)]
    )


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
