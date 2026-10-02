# YouTube Blog Generator with CrewAI

A small CrewAI multi-agent project that researches videos from a configured YouTube channel and turns a selected lecture name into a Markdown blog post. Streamlit displays the submitted input, research result, and final blog. The agents use Google Gemini for text generation.

> **Current behavior:** this project searches the configured YouTube channel by lecture name; it does not upload or read a local video file.

## How It Works

The crew runs two agents sequentially:

![](project%20flow%20diagram.png)

1. **Blog researcher** uses the YouTube channel search tool to find information for the requested topic and prepares a short research report.
2. **Blog writer** uses the research result to draft a readable blog post.
3. Streamlit displays the research and final blog, with an option to download the blog as Markdown.

The YouTube search tool uses the channel ID configured in `tools.py`. YouTube search embeddings use Chroma's local ONNX model; `GEMINI_API_KEY` is used for Gemini text generation.

## Run on Windows

Open PowerShell in the project folder. Create and activate the virtual environment if you do not already have one:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` only if `.env` does not already exist, then ensure it contains your Gemini API key and model:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini/gemini-3.8-flash
```

Keep your real key private. `.env` is ignored by Git; do not commit it or paste the key into source code. Set `GEMINI_MODEL_NAME` to a Gemini model available to your account.

Launch Streamlit from the project folder:

```bash
python -m streamlit run app.py
```

Open the Local URL printed by Streamlit (usually `http://localhost:8501`). Enter a lecture name. The app searches the configured channel and displays the input, each task's output, and the final blog.

## Customize the Run

- **YouTube channel:** change the channel ID URL in `tools.py` and keep the ONNX embedding configuration to match the persisted collection.
- **Model:** set `GEMINI_MODEL_NAME` in `.env` to a Gemini model available to your account.

The current search is channel-based. Supporting an uploaded/local video or selecting an arbitrary video URL requires changing the YouTube tool and the task input flow.

## Project Structure

| File | Purpose |
| --- | --- |
| `agents.py` | Defines the researcher and writer agents and their Gemini LLM. |
| `tasks.py` | Builds the research and writing tasks for each run. |
| `tools.py` | Configures channel search and local ONNX embeddings. |
| `crew.py` | Creates and runs the sequential crew for a topic. |
| `app.py` | Streamlit UI for lecture input, task output, and blog display. |
| `requirements.txt` | Python dependencies installed into `venv`. |
| `.env.example` | Template for Google Gemini configuration; copy to `.env`. |

## Troubleshooting

- **`GEMINI_API_KEY must be set`:** confirm `.env` exists in the project directory and contains a valid `GEMINI_API_KEY` entry. Restart the app after editing it.
- **Authentication or model error:** verify the key in Google AI Studio and confirm `GEMINI_MODEL_NAME` is available to your account.
- **Rate limit or quota error:** check your Google AI account's current usage limits.
- **No relevant video found:** check the channel ID URL in `tools.py`, the lecture name entered in the app, and that the channel has matching videos accessible to the search tool.
- **`regex` or `tiktoken` build errors:** use Python 3.12 and create the `venv` environment with `py -3.12 -m venv venv`. Changing the Python version does not change an environment that was already created.
- **Import errors:** activate `venv` and install dependencies with `python -m pip install -r requirements.txt` from the project directory.

## Security

Never commit `.env` or expose your Gemini API key in logs, screenshots, source code, or public issue reports. If a key is exposed, revoke it and create a replacement.
