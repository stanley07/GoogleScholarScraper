import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scraper.google_scholar_scraper import scrape_google_scholar
from scraper.utils import get_tags, extract_paper_info

# Function to send an email using SMTP
def send_email(sender_email, sender_password, receiver_email, subject, message):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server
    with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Define the sender's email and password
sender_email = 'chidost@yahoo.com'
sender_password = 'Mission_2022'

# Define the receiver's email
receiver_email = 'ezebo001@gmail.com'

# Define the keyword for searching papers
keyword = 'Solar Energy'

# Specify the number of pages to scrape
num_pages = 10

# Scrape Google Scholar and retrieve the paper information
papers = scrape_google_scholar(keyword, num_pages)

# Create the email message
message = 'Here are some recommended research papers on Solar Energy:\n\n'
for paper in papers:
    message += f'Title: {paper["Title"]}\n'
    message += f'Authors: {paper["Author"]}\n'
    message += f'Citation Count: {paper["Citation Count"]}\n'
    message += f'URL: {paper["URL"]}\n\n'

# Send the email to the receiver
send_email(sender_email, sender_password, receiver_email, 'Research Paper Recommendations', message)
