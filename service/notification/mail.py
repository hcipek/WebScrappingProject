from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

from variables import SendGridVariables as Variables


class MailService:
    def __init__(self):
        self.sendgrid = SendGridAPIClient(api_key=Variables.API_KEY)
        self.from_email = Email(Variables.FROM_EMAIL)
        self.to_email = To(Variables.TO_EMAIL)

    def send_mail(self, subject: str, content_mime: str, content_ctx: str):
        content = Content(content_mime, content_ctx)
        mail = Mail(self.from_email, self.to_email, subject, content)
        response = self.sendgrid.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
