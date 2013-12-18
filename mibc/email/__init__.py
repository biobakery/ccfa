
import smtplib
from email.mime.text import MIMEText

from bottle import SimpleTemplate

import settings

def render_to_email(subject, context, address_list, 
                    template="notification.tpl", **kwargs):
    """send an email to someone by rendering a template with 
    the provided context (a dictionary).
    **kwargs are fitted into the fields of the message
    """

    for k, v in { "To":      address_list,
                  "From":    settings.email.default_from_addr,
                  "Subject": settings.email.default_subject, }:
        kwargs.setdefault(k, v)

    msg = SimpleTemplate(template, **context).render()
    msg = MIMEText(msg)
    msg.update(kwargs)

    s = smtplib.SMTP(settings.email.default_smtp_serv)
    s.sendmail( kwargs["From"], address_list, msg.as_string() )
    s.quit()
