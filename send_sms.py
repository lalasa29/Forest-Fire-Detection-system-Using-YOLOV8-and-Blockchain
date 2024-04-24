from twilio.rest import Client

# Twilio credentials

account_sid = ''
auth_token = ''
twilio_phone_number = ''
  
to_phone = 'insert phone number'




def send_sms(message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=message,
                     from_=twilio_phone_number,
                     to=to_phone
                 )
send_sms('Hello, this is a test message.')