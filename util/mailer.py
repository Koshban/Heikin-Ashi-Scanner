import ssl
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import *


text_bear_rev = """

Stocks showing reversal after falling for X days:

"""

text_free_fall = """

Stocks in free fall:

"""

text_aggregated = """

Aggregated table

"""

text_bollinger = """

Stocks in Bollinger scan:

"""

text_ema_x = """

Stocks near SMA 100 or 200:

"""

html = """\
<html>
  <body>
{0}
  </body>
</html>
"""


def sendmail(signal_list, mode):
    my_message_to = Mode.message_to(mode)
    print("Mode = {0} so sending mail to : {1}".format(mode, message_to))
    message = MIMEMultipart("mixed")
    message["From"] = message_from
    message["To"] = my_message_to
    message["Subject"] = Mode.subject(mode)
    part1 = MIMEText(text_bear_rev, "plain")
    part2 = MIMEText(html.format(signal_list[0]), "html")
    message.attach(part1)
    message.attach(part2)

    part3 = MIMEText( text_ema_x, "plain")
    part4 = MIMEText(html.format(signal_list[1]), "html")
    message.attach(part3)
    message.attach(part4)

    part5 = MIMEText(text_bollinger, "plain")
    part6 = MIMEText(html.format(signal_list[2]), "html")
    message.attach(part5)
    message.attach(part6)

    part7 = MIMEText(text_free_fall, "plain")
    part8 = MIMEText(html.format(signal_list[3]), "html")
    message.attach(part7)
    message.attach(part8)

    # part9 = MIMEText( text_aggregated, "plain")
    # part10 = MIMEText(html.format(signal_list[4]), "html")
    # message.attach(part9)
    # message.attach(part10)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender, password)
        server.sendmail(sender, my_message_to.split(","), message.as_string() )
