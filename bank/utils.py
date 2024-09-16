from twilio.rest import Client

def send_sms(to, body):
    client = Client("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")
    message = client.messages.create(
        to=to,
        from_="TWILIO_PHONE_NUMBER",
        body=body
    )