# B.R.A.I.N - Browser Retrieval and Automation Intelligent Network

**B.R.A.I.N.** is an advanced AI-powered system that transforms browser automation through natural language prompts. By integrating Google's Gemini LLM for deep instruction comprehension and Playwright for reliable web automation, it can intelligently navigate websites, extract data, and execute complex tasks.

## Key Features

- **Natural Language Control**: Automate web tasks by giving commands in plain English.
- **Data Extraction**: Gather and structure information from websites automatically.
- **Repetitive Task Automation**: Automate tedious online chores like filling out forms or checking for updates.
- **Intelligent and Adaptable**: Leverages AI to understand context and adapt to different website structures.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    - Create a file named `.env` in the project folder.
    - Add your Gemini API key to this file like so: `GEMINI_API_KEY="YOUR_API_KEY_HERE"`

5.  **Run the application:**
    ```bash
    python app.py
    ```