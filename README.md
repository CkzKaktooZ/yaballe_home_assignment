Welcome to the Yaballee BlogPost API 🎉
Instructions to Run the API:

    ✅ Make sure you have Python 3.12 or higher installed (we recommend 3.12 specifically).

    🛡️ (Optional but recommended) Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate # On Linux/macOS
.venv\Scripts\activate # On Windows

📦 Install dependencies:

pip install -r requirements.txt

🚀 Run the API:

python -m src.main

🌐 Open your browser and go to:

    http://localhost:8080/docs

    to use the interactive Swagger UI for testing and exploring the API.

🧪 Running Tests with Pytest

We use pytest for automated testing.
To run all tests:

pytest

To run a specific test file:

pytest tests/test_users.py

To see detailed output:

pytest -v

To run tests and show print/log outputs:

pytest -s

    Make sure your test database is configured properly if you're mocking or using SQLite, and that the tables are created for test runs.

Enjoy developing! 🙌 If you have any questions or bugs, feel free to improve this project further.
