# Yaballee BlogPost API

Welcome to the **Yaballee BlogPost API** – a simple blog platform with user registration, authentication, post creation, and voting functionality.

---

## 🚀 How to Run the API

### 1. Prerequisites

- Python **3.12** or higher installed (this project uses 3.12)

### 2. Setup

#### (Optional) Create a virtual environment

```bash
python -m venv .venv
# Activate the virtual environment:
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
# Install Dependencies:
pip install -r requirements.txt
```

### 3. Start the API

```bash
python -m src.main
```

- Once the server is running, open your browser and go to:

```bash
http://localhost:8080/docs
```

This will open the Swagger UI for interactive API testing and documentation.

---

## 🧪 Running Tests with Pytest

This project uses [`pytest`](https://docs.pytest.org/) for testing.

### ✅ To run all tests:

```bash
pytest
```

- Let me know if you'd like to include examples of test output or how to use fixtures!
