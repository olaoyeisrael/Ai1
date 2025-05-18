import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv(override=True)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))
        print("1")
    

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        # print(EMAIL_PORT)
        server.starttls()
    
        server.login(EMAIL_USER, EMAIL_PASS)

        print("3")
        server.send_message(msg)
        # with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        #     server.login(EMAIL_USER, EMAIL_PASS)
        #     server.send_message(msg)

        print(f"[MAILER] Email sent to {to_email}")

    except Exception as e:
        print(f"[MAILER ERROR] Failed to send email: {e}")


# import os
# import resend
# from dotenv import load_dotenv 

# load_dotenv()

# resend.api_key = os.getenv("RESEND_API_KEY")

# def send_email(to_email: str, subject: str, body: str):
    
#     try:
#         params: resend.Emails.SendParams = {
#             "from": "AI Tutor <noreply@aitutor.com>",
#             "to": [to_email],
#             "subject": subject,
#             "html": body
#         }

#         result = resend.Emails.send(params)
#         print(f"[MAILER ✅] {result}")
#         return result
#     except Exception as e:
#         print(f"[MAILER ERROR] {e}")
#         return None

# import sib_api_v3_sdk
# from sib_api_v3_sdk.rest import ApiException
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # configuration = sib_api_v3_sdk.Configuration()
# # configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
# configuration = sib_api_v3_sdk.Configuration()
# configuration.api_key['api-key'] = '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'

# # sib_api_v3_sdk.configuration.api_key['api-key'] = 

# # api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
# api_instance = sib_api_v3_sdk.EmailCampaignsApi()

# def send_email(to_email: str, subject: str, body: str):
#     try:
#         print("1")  # Step marker

#         # Set sender details from .env
#         sender = {
#             "name": os.getenv("BREVO_SENDER_NAME", "AI Tutor"),
#             "email": os.getenv("BREVO_SENDER_EMAIL")
#         },
        

#         # Prepare email structure
#         send_smtp_email = sib_api_v3_sdk.CreateEmailCampaign(
#             name= os.getenv("BREVO_SENDER_NAME", "AI Tutor"),
#             sender= sender,
#             type= "classic",
#             subject=subject,
#             html_content=body
#         )

#         print("2")  # Step marker

#         # Send the email
#         response = api_instance.create_email_campaign(send_smtp_email)

#         print("3")  # Step marker
#         print(f"[MAILER ✅] Email sent to {to_email}")
#         print(response)

#     except ApiException as e:
#         print(f"[MAILER ERROR ❌] Failed to send email: {e}")


        