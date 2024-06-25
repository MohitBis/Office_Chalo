import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App, Ack

from slack_sdk import WebClient
client = WebClient(token="token")


from slack_bolt.adapter.socket_mode import SocketModeHandler


app = App(token="token")

responses = {}
channel_id = ""


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    global channel_id
    logger.debug(body)
    user = None
    decision = None
    if "user" in body.keys():
        user = body["user"]["name"]
    if "submission" in body.keys():
        decision =  body["submission"]["types"]
    if "channel" in body.keys():
        channel_id = body["channel"]["id"]

    if user and decision:
        responses[user] =  decision
        if decision == "No":
            text = "Thank you for your response"
            client.chat_postMessage(
                channel=channel_id,
                text=text
                )
        else:
            text = str(sum(1 for value in responses.values() if value != "No"))
            client.chat_postMessage(
                channel=channel_id,
                text=text
                )         

    return next()


@app.action("dialog-callback-id")
def dialog_submission_or_cancellation(ack: Ack, body: dict):
    if body["type"] == "dialog_cancellation":
        ack()
        return

    errors = []

    if len(errors) > 0:
        ack(errors=errors)
    else:
        ack()

@app.options("dialog-callback-id")
def dialog_suggestion(ack):
    ack(
        {
            "options": [
                {
                    "label": "Red Hat office 1",
                    "value": "RH 1",
                },
                {
                    "label": "Red Hat office 2",
                    "value": "RH 2",
                },
                {
                    "label": "Red Hat office 3",
                    "value": "RH 3",
                },
                {
                    "label": "Not coming",
                    "value": "No",
                },
            ]
        }
    )

@app.command("/office-chalo")
def test_command(body, client, ack, logger):
    logger.info(body)
    res = client.dialog_open(
        trigger_id=body["trigger_id"],
        dialog={
            "callback_id": "dialog-callback-id",
            "title": "Coming to office?",
            "submit_label": "Request",
            "notify_on_cancel": True,
            "state": "Limo",
            "elements": [
                {
                    "label": "Please select your option",
                    "name": "types",
                    "type": "select",
                    "data_source": "external",
                },
            ],
        },
    )
    logger.info(res)


if __name__ == "__main__":
    SocketModeHandler(app, "token").start()
