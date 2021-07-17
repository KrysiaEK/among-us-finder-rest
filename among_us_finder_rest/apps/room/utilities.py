from django.core.mail import mail_admins


def send_mail_to_admins(message):
    subject = "Abuse report"
    mail_admins(subject, message)
