#!/bin/bash
aws --endpoint-url http://localhost:5000 ses verify-domain-identity --domain example.com
aws --endpoint-url http://localhost:5000 ses verify-email-identity --email me@example.com
aws --endpoint-url http://localhost:5000 ses send-email --from me@example.com --to to@example.com --subject Test --text Hello
aws --endpoint-url http://localhost:5000 ses send-raw-email --raw-message file://raw_mail.json
curl http://localhost:5000/message/to@example.com
