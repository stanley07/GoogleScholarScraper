from flask import Flask, render_template, request, redirect
import sqlite3
from scholarly import scholarly
import smtplib
import traceback
import threading
import requests
import os
from email.message import EmailMessage

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
                interests TEXT NOT NULL
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
        cursor.execute('INSERT INTO user (name, email, interests) VALUES (?, ?, ?)', (name, email, interests))
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


def create_email_content(name, email, interests):
    subject = "Registration Successful"
    body = f"Dear {name},\n\nThank you for registering!\n\nYour email: {email}\nYour interests: {interests}\n\n"
    body += "Here are the research papers related to your interests:\n"
    for filename in os.listdir('.'):
        if filename.endswith('.pdf'):
            body += f"- {filename}\n"
    body += "\nBest regards,\nThe Example App Team"
    return subject, body


def send_email_async(email, subject, content, attachment_filenames):
    try:
        message = EmailMessage()
        message['From'] = SMTP_USERNAME
        message['To'] = email
        message['Subject'] = subject
        message.set_content(content)

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
        print("Register route called")

        name = request.form.get('name')
        email = request.form.get('email')
        interests = request.form.get('interests')

        print(f"Name: {name}, Email: {email}, Interests: {interests}")

        # Store user details in the database
        if name and email and interests:
            insert_user(name, email, interests)

            # Send email asynchronously
            subject, email_content = create_email_content(name, email, interests)

            attachment_filenames = []
            for filename in os.listdir('.'):
                if filename.endswith('.pdf'):
                    attachment_filenames.append(filename)

            thread = threading.Thread(target=send_email_async, args=(email, subject, email_content, attachment_filenames))
            thread.start()

            # Email sent successfully
            return redirect(f'/success?email={email}&interests={interests}&status=success')

        # If any required field is missing, redirect back to the index page
        return redirect('/')

    except Exception as e:
        print(f"Error occurred in register route: {str(e)}")
        traceback.print_exc()


@app.route('/users')
def view_users():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        conn.close()
        return render_template('users.html', users=users)
    except sqlite3.Error as e:
        print(f"Error occurred while fetching users: {str(e)}")
        traceback.print_exc()


if __name__ == '__main__':
    create_user_table()
    app.run(debug=True, port=5008)
