from flask import Flask, render_template, request, redirect
import sqlite3
from scholarly import scholarly
import smtplib
import traceback
import datetime
import threading
import requests
import time
from email.message import EmailMessage
import schedule

app = Flask(__name__)

# SMTP Configuration
SMTP_HOST = 'smtp-mail.outlook.com'
SMTP_PORT = 587
SMTP_USERNAME = 'ezebo001@outlook.com'  # Update with your Outlook email address
SMTP_PASSWORD = 'uoipfbsohdreooqd'  # Update with your Outlook password

def create_user_table():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                interests TEXT NOT NULL,
                last_sent_email TEXT DEFAULT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred while creating user table: {str(e)}")
    finally:
        if conn:
            conn.close()

def insert_user(name, email, interests):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user (name, email, interests, last_sent_email) VALUES (?, ?, ?, ?)',
                       (name, email, interests, datetime.datetime.now()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred while inserting user: {str(e)}")
    finally:
        if conn:
            conn.close()

def fetch_research_papers(query):
    try:
        search_query = scholarly.search_pubs(query)
        papers = []
        for i in range(5):  # Fetch the top 5 papers
            try:
                paper = next(search_query)
                if isinstance(paper, dict) and 'bib' in paper:
                    title = paper['bib'].get('title')
                    citation_count = paper['bib'].get('cites', 0)
                    authors = paper['bib'].get('author', '')
                    url = paper['pub_url'] if 'pub_url' in paper else ''
                    if title:
                        papers.append({
                            'Title': title,
                            'Citation Count': citation_count,
                            'Authors': authors,
                            'URL': url
                        })
            except Exception as e:
                print(f"Error occurred while fetching paper: {str(e)}")
                traceback.print_exc()
        return papers
    except Exception as e:
        print(f"Error occurred while fetching research papers: {str(e)}")
        return []

def download_paper(url, title):
    try:
        response = requests.get(url)
        filename = f"{title}.pdf"
        with open(filename, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(f"Error occurred while downloading paper: {str(e)}")

def create_email_content(name, email, interests, papers):
    subject = "Registration Successful"
    body = f"Dear {name},<br><br>Thank you for registering!<br><br>"
    body += f"Your email: {email}<br>Your interests: {interests}<br><br>"

    # Fetch the success page HTML
    success_page_url = 'http://127.0.0.1:8000/success'
    params = {'email': email, 'interests': interests, 'status': 'success'}
    response = requests.get(success_page_url, params=params)
    success_page_html = response.text

    body += success_page_html

    # Calculate the next weekly update date
    today = datetime.date.today()
    weekday = today.weekday()  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
    days_until_next_update = (6 - weekday) % 7  # Calculate the number of days until the next Monday
    next_update_date = today + datetime.timedelta(days=days_until_next_update)
    next_update_date_str = next_update_date.strftime("%A, %B %d, %Y")

    body += f"<br>You will receive your next weekly update on {next_update_date_str}.<br><br>"
    body += "<br>Best regards,<br>The Example App Team"
    return subject, body

def send_email(email, subject, content, attachment_filenames):
    try:
        message = EmailMessage()
        message['From'] = SMTP_USERNAME
        message['To'] = email
        message['Subject'] = subject
        message.set_content(content, subtype='html')

        for filename in attachment_filenames:
            with open(filename, 'rb') as file:
                file_data = file.read()
                message.add_attachment(file_data, maintype='application', subtype='pdf', filename=filename)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

    except smtplib.SMTPException as e:
        print(f"Error occurred while sending email: {str(e)}")
        traceback.print_exc()

def send_weekly_emails():
    # Fetch research papers for all registered users
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()

    for user in users:
        name, email, interests, last_sent_email = user
        papers = fetch_research_papers(interests)

        if last_sent_email:
            last_sent_email = datetime.datetime.strptime(last_sent_email, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.datetime.now()
            time_diff = current_time - last_sent_email
            if time_diff.days < 7:
                continue

        email_content = create_email_content(name, email, interests, papers)
        attachment_filenames = []
        for paper in papers:
            title = paper.get('Title', '')
            url = paper.get('URL', '')
            if url:
                download_paper(url, title)
                attachment_filenames.append(f"{title}.pdf")
        send_email(email, *email_content, attachment_filenames)

        # Update the last_sent_email field in the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET last_sent_email = ? WHERE email = ?', (datetime.datetime.now(), email))
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def success():
    try:
        email = request.args.get('email')
        interests = request.args.get('interests')
        status = request.args.get('status')

        # Fetch research papers based on user interests
        papers = fetch_research_papers(interests)

        message = ''
        if status == 'success':
            message = 'Email sent successfully!'
        elif status == 'failure':
            message = 'Failed to send email. Please try again.'

        return render_template('success.html', email=email, interests=interests, papers=papers, message=message)
    except Exception as e:
        print(f"Error occurred in success route: {str(e)}")
        traceback.print_exc()

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        email = request.form['email']
        interests = request.form['interests']

        insert_user(name, email, interests)

        return redirect(f"/success?email={email}&interests={interests}&status=success")
    except Exception as e:
        print(f"Error occurred in register route: {str(e)}")
        traceback.print_exc()
 
        return redirect(f"/success?email={email}&interests={interests}&status=failure")

@app.route('/users')
def view_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)


def start_weekly_email_scheduler():
    schedule.every().monday.at("09:00").do(send_weekly_emails)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    create_user_table()

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=start_weekly_email_scheduler)
    scheduler_thread.start()

    app.run(debug=False, port=8000)

