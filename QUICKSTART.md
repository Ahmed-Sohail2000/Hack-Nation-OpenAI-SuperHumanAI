# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up OpenAI API Key

Edit `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
```

## 3. Process Emails (if not done already)

```bash
python process_emails.py
```

## 4. Run the Application

### Option A: CLI Interface
```bash
python app.py
```

### Option B: Web Interface
```bash
python run_api.py
```
Then open: http://localhost:5000

## Example Queries

- "Who are the top communicators?"
- "What are the main topics discussed?"
- "Analyze communication patterns"
- "Who communicates most with [person]?"

## Troubleshooting

- **No module named 'openai'**: Run `pip install -r requirements.txt`
- **OpenAI API key error**: Check your `.env` file has `OPENAI_API_KEY` set
- **emails.json not found**: Run `python process_emails.py` first
- **Port already in use**: Change `PORT` in `.env` file
