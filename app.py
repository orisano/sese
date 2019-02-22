import argparse
import typing

import flask
import moto.server
import moto.ses
import moto.ses.models

app: flask.Flask = moto.server.create_backend_app("ses")


@app.route("/message/<destination>", methods=["GET"])
def get_email(destination: str):
    messages: typing.List[moto.ses.models.Message] = moto.ses.ses_backend.sent_messages
    return flask.jsonify(
        [
            {"source": msg.source, "subject": msg.subject, "body": msg.body}
            for msg in messages
            if any(destination in v for v in msg.destinations.values())
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H", "--host", type=str, help="Which host to bind", default="127.0.0.1"
    )
    parser.add_argument(
        "-p", "--port", type=int, help="Port number to use for connection", default=5000
    )
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
