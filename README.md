# 🎭 Joke Engine

**Joke Engine** is a Django-based GenAI application that generates custom jokes on any topic using OpenAI's GPT models. It features a history tracking system, local caching to save API costs, and a clean Bootstrap UI.

![Architecture](https://img.shields.io/badge/Architecture-Django_MVC-green)
![AI](https://img.shields.io/badge/AI-OpenAI_GPT--3.5-blue)

## 🚀 Features

*   **AI-Powered Humor:** Generates unique jokes based on user input topics.
*   **Smart Caching:** Checks the local database for existing jokes before calling the API to reduce latency and costs.
*   **History Tracking:** View previously generated jokes with pagination.
*   **Management:** Delete old jokes from the history.
*   **Responsive UI:** Clean interface built with Bootstrap 5.

**New Features Added / Planned**

- **Comedian Persona:** Choose a style (`witty`, `dad`, `sarcastic`, `roast`, `haiku`) from the search form. The backend adjusts the system prompt to match the persona.
- **Smart Caching by Style:** Results are cached using a composite query key (e.g., `Cats [dad]`) so different styles are stored separately.
- **Regenerate / Remix:** A "Regenerate" button forces a fresh API call, bypassing the local cache when you want a new variation.
- **Live Mic (TTS):** A small "Listen" button uses the browser Web Speech API to read jokes aloud.
- **Copy to Clipboard:** Quickly copy jokes to share with one click.

See the `giggle/` templates and views for usage details. Run `python manage.py makemigrations` and `python manage.py migrate` after pulling changes if you updated the models.

## 🛠️ Tech Stack

*   **Backend:** Python, Django 4.x
*   **AI Engine:** OpenAI API (GPT-3.5-turbo)
*   **Database:** SQLite (Default)
*   **Frontend:** HTML5, CSS3, Bootstrap 5
*   **Configuration:** Python-Decouple

## 📂 Project Structure

```text
dhananjaylab-joke-engine/
├── giggle/              # Main App Logic (Views, Models, APIs)
├── project/             # Project Settings & Config
├── manage.py            # Django Entry Point
├── db.sqlite3           # Local Database
└── .env                 # Secrets (Not committed)
```

⚡ Getting Started

Follow these steps to set up the application locally.

### Prerequisites

Python 3.8 or higher

An OpenAI API Key (Get one here)

1. Clone the Repository

```bash
git clone https://github.com/dhananjaylab/joke-engine.git
cd dhananjaylab-joke-engine
```

2. Create Virtual Environment

It is recommended to use a virtual environment.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies

Create a requirements.txt file (if not present) with the following content, then install:

requirements.txt:

```text
Django>=4.2.3
openai>=0.27.0
python-decouple>=3.8
```

Install:

```bash
pip install -r requirements.txt
```

4. Configure Environment Variables

Create a .env file in the root directory (same level as manage.py) and add your OpenAI key:

```ini
CHATGPT_API_KEY=sk-your-openai-api-key-here
DEBUG=True
SECRET_KEY=your-secret-key-for-dev
```

5. Database Migration

Initialize the SQLite database.

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Run the Application

```bash
python manage.py runserver
```

Open your browser and navigate to:
👉 http://127.0.0.1:8000/

## 📖 Usage Guide

Search: Enter a topic (e.g., "Programmers", "Pizza", "Cats") in the search bar.

Read: The AI will generate a joke. If you search the same topic again, it pulls from the database instantly.

History: Click "See history" to view all past jokes.

Delete: Use the trash icon in the history view to remove jokes you don't like.

## 🤝 Contributing

Fork the repository.

Create a new feature branch (git checkout -b feature/AmazingFeature).

Commit your changes.

Push to the branch.

Open a Pull Request.

## 📝 License

Distributed under the MIT License.

### Part 4: Essential Missing File

You must add a `requirements.txt` file to the root of the repository for the application to run on other machines.

**File:** `requirements.txt`
```text
asgiref==3.7.2
Django==4.2.3
openai==0.27.8
python-decouple==3.8
sqlparse==0.4.4
typing_extensions==4.7.1
```
