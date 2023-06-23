


from flask import Flask, render_template, request, redirect
import sqlite3
from scholarly import scholarly
import smtplib

app = Flask(__name__)

# SMTP Configuration
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'ezebo001@gmail.com'  # Update with your Gmail email address
SMTP_PASSWORD = 'nmimdoqclbujejkt'  # Update with your Gmail password

# SMTP Configuration
SMTP_HOST = 'smtp-mail.outlook.com'
SMTP_PORT = 587
SMTP_USERNAME = 'ezebo001@outlook.com'  # Update with your Gmail email address
SMTP_PASSWORD = 'uoipfbsohdreooqd'  # Update with your Gmail password



def create_user_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            interests TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insert_user(email, interests):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user (email, interests) VALUES (?, ?)', (email, interests))
    conn.commit()
    conn.close()


def fetch_research_papers(query):
    try:
        search_query = scholarly.search_pubs(query)
        papers = []
        for i in range(5):  # Fetch the top 5 papers
            paper = next(search_query)
            if isinstance(paper, dict) and 'bib' in paper:
                title = paper['bib'].get('title')
                citation_count = paper['bib'].get('cites', 0)
                author = paper['bib'].get('author', '')
                url = paper['pub_url'] if 'pub_url' in paper else ''
                if title:
                    papers.append({
                        'Title': title,
                        'Citation Count': citation_count,
                        'Author': author,
                        'URL': url
                    })
        return papers
    except Exception as e:
        # Log the exception or handle it as desired
        print(f"Error occurred while fetching research papers: {str(e)}")
        return []  # Return an empty list in case of error


def send_email(email, papers):
    subject = 'Research Papers Recommendation'
    body = f"Dear user,\n\nHere are some research papers based on your interests:\n\n"
    for paper in papers:
        title = paper['Title']
        citation_count = paper['Citation Count']
        author = paper['Author']
        url = paper['URL']
        body += f"Title: {title}\nCitation Count: {citation_count}\nAuthor: {author}\nURL: {url}\n\n"
    body += "\n\nThank you!\n"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, message)
    except Exception as e:
        # Log the exception or handle it as desired
        print(f"Error occurred while sending email: {str(e)}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    interests = request.form.get('interests')

    # Check if the email is provided
    if not email:
        return render_template('index.html', error="Email is required.")

    # Fetch research papers based on user interests
    papers = fetch_research_papers(interests)

    # Store user details in the database
    insert_user(email, interests)

    # Send email to the user with the research papers recommendation
    send_email(email, papers)

    return redirect('/', code=302)


@app.route('/users')
def view_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)


if __name__ == '__main__':

    app.run(debug=True, port=5008)