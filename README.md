# Scholar Messenger

Scholar Messenger is a research-focused web application designed to facilitate knowledge sharing, collaboration, and paper recommendations among scholars and researchers. It provides a platform for researchers to connect with peers, discover relevant research papers, and engage in meaningful discussions within their academic community.

## Features

- **User Registration and Profiles**: Users can create accounts, set up their profiles, and define their research interests to receive personalized recommendations and connect with like-minded scholars.

- **Paper Recommendations**: Scholar Messenger utilizes the IEEE API to fetch research papers based on user interests. Users can explore recommended papers, view abstracts, authors, and access full-text articles when available.

- **Real-Time Notifications**: Users receive real-time notifications about new papers, collaboration requests, and important deadlines, ensuring they stay updated within their research community.

- **Mobile-Friendly Design**: Scholar Messenger is responsive and optimized for mobile devices, allowing users to access the platform conveniently on their smartphones and tablets.

## Technologies Used

- Flask: Python-based web framework used for server-side development.
- SQLite: Lightweight relational database management system for data storage.
- HTML/CSS: Front-end development technologies for creating the user interface and styling.
- JavaScript: Programming language used for interactive elements and client-side functionality.
- Flask-Mail: Extension for Flask to handle email sending functionality.
- Requests: Python library for making HTTP requests to the IEEE API.

## Installation

1. Clone the repository: `git clone https://github.com/stanley07/GoogleScholarScraper.git`
2. Navigate to the project directory: `cd scholar-messenger`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Set up your SMTP configuration in the `app.py` file.
5. Run the application: `python app.py`
6. Access the application in your browser at `http://localhost:5000`

Note: Make sure you have Python 3.x and pip installed on your system.

## Contributing

We welcome contributions from the open-source community to enhance Scholar Messenger. If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature-name`
3. Implement your changes and ensure they are well-tested.
4. Commit your changes: `git commit -m "Add feature"`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request explaining your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

We would like to express our gratitude to the creators and contributors of the libraries and frameworks used in this project. Their work is invaluable and greatly appreciated.

## Contact

For any inquiries or support, please contact us at [ezebo001@gmail.com]

Thank you for your interest in Scholar Messenger!
