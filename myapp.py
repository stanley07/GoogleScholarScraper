from flask import Flask, render_template, request, redirect, render_template_string
from flask_mail import Mail, Message
import sqlite3
import requests
import datetime
import traceback
import threading
import schedule
import time

app = Flask(__name__)

# SMTP Configuration
SMTP_HOST = 'smtp-mail.outlook.com'
SMTP_PORT = 587
SMTP_USERNAME = 'ezebo001@outlook.com'  # Update with your Outlook email address
SMTP_PASSWORD = 'uoipfbsohdreooqd'  # Update with your Outlook password

# Database Configuration
DATABASE = 'database.db'

# IEEE API Configuration
API_KEY = 'xr3m4esj7zek56daaj6a4wxz'
BASE_URL = 'https://ieeexploreapi.ieee.org/api/v1/search/articles'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = SMTP_HOST
app.config['MAIL_PORT'] = SMTP_PORT
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = SMTP_USERNAME
app.config['MAIL_PASSWORD'] = SMTP_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = SMTP_USERNAME

mail = Mail(app)


def create_user_table():
    try:
        conn = sqlite3.connect(DATABASE)
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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO user (name, email, interests, last_sent_email) VALUES (?, ?, ?, ?)',
            (name, email, interests, datetime.datetime.now())
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred while inserting user: {str(e)}")
    finally:
        if conn:
            conn.close()


def fetch_research_papers(query):
    params = {
        'apikey': API_KEY,
        'querytext': query,
        'max_results': 5,  # Adjust the number of results as needed
        'sort_order': 'asc',  # Sort order: ascending
        'sort_field': 'article_title'  # Sort by article title
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if 'articles' in data:
            papers = data['articles']
            result = []
            for paper in papers:
                title = paper['title']
                authors = ', '.join(paper['authors'])
                abstract = paper.get('abstract')
                doi = paper.get('doi', '')  # Check if the 'doi' field is present
                url = f"https://doi.org/{doi}" if doi else ''  # Generate URL based on DOI if available

                # Append the retrieved paper information to the result list
                result.append({
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'doi': doi,
                    'url': url
                })

            return result[:10]  # Return only the first 10 papers
        else:
            print("No articles found.")
            return []

    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return []


def send_email(recipient, subject, body):
    with app.app_context():
        msg = Message(subject, recipients=[recipient])
        msg.html = body  # Set the email body as HTML
        mail.send(msg)


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
        papers = fetch_research_papers(interests)[:10]  # Limit the papers to 10

        # Send papers as an email to the user
        email_subject = 'Research Papers Recommendation'
        email_body = render_template('email_template.html', papers=papers)  # Updated template name
        send_email(email, email_subject, email_body)

        # Get recommended papers based on user's previous interests
        recommended_papers = []
        previous_interests = get_user_interests(email)
        if previous_interests:
            recommended_papers = fetch_research_papers(previous_interests)[:3]  # Limit the recommended papers to 3

        message = ''
        if status == 'success':
            message = 'Email sent successfully!'
        elif status == 'failure':
            message = 'Failed to send email. Please try again.'

        success_page_url = request.url_root + 'success'  # Update the URL here
        return render_template(
            'success.html',
            email=email,
            interests=interests,
            papers=papers,
            recommended_papers=recommended_papers,
            message=message,
            success_page_url=success_page_url
        )
    except Exception as e:
        print(f"Error occurred in success route: {str(e)}")
        traceback.print_exc()


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            interests = request.form['interests']

            insert_user(name, email, interests)

            return redirect(f"/success?email={email}&interests={interests}&status=success")

        # Handle GET requests to display the registration form
        return render_template('register.html')

    except Exception as e:
        print(f"Error occurred in register route: {str(e)}")
        traceback.print_exc()
        return redirect(f"/success?email={email}&interests={interests}&status=failure")


@app.route('/users')
def view_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)


def get_user_interests(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT interests FROM user WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def send_weekly_emails():
    # Fetch users from the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()

    # Send email to each user
    for user in users:
        email = user[2]
        interests = user[3]

        # Fetch research papers based on user interests
        papers = fetch_research_papers(interests)

        # Send email to the user
        email_subject = 'Weekly Research Papers Recommendation'
        email_body = render_template('email_template.html', papers=papers)  # Updated template name
        send_email(email, email_subject, email_body)

        # Update the last sent email time for the user
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET last_sent_email = ? WHERE email = ?', (datetime.datetime.now(), email))
        conn.commit()
        conn.close()


def schedule_weekly_emails():
    # Schedule the weekly email job
    schedule.every().monday.at('09:00').do(send_weekly_emails)  # Update the day and time as needed

    # Start the scheduler in a separate thread
    thread = threading.Thread(target=run_scheduler)
    thread.start()


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    create_user_table()
    schedule_weekly_emails()
    app.run(debug=True)
