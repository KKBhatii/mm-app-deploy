from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from users.models import User


# to send the verification mail to the user
def send_verification_mail(send_to:str,user:User,verification_url:str)->bool:
    try:
        subject, from_email = "Verification mail", "auth@marketmate.in"
        text_content = "Verify Yourself."
        html_content=render_to_string("mail/user_verification.html",{"user":user,"verification_url":verification_url})
        mail=EmailMultiAlternatives(subject=subject,body=text_content,from_email=from_email,to=[send_to])
        mail.attach_alternative(content=html_content,mimetype="text/html")
        mail.send()
        return True
    except Exception as e:
        return False
    
# to send the notification mail to the user
def send_notification_mail(send_to:str,user:User,item_url:str,recipient:str)->bool:
    try:
        subject, from_email = "Someone interested in your item", "marketmatedev@mm.in"
        html_content=render_to_string("mail/listing_item_notification.html",{"user":user,"item_url":item_url,"recipient_name":recipient})
        mail=EmailMultiAlternatives(subject=subject,from_email=from_email,to=[send_to])
        mail.attach_alternative(content=html_content,mimetype="text/html")
        mail.send()
        return True
    except Exception as e:
        return False

