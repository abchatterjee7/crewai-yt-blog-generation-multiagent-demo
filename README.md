# YouTube Blog Generator with CrewAI

A small CrewAI multi-agent project that researches videos from a configured YouTube channel and turns a selected topic into a Markdown blog post. The agents use a Groq-hosted language model for text generation.

> **Current behavior:** this project searches a YouTube channel; it does not upload or read a local video file. The channel handle and topic are currently configured in Python files.

## How It Works

The crew runs two agents sequentially:

![](project%20flow%20diagram.png)

1. **Blog researcher** uses the YouTube channel search tool to find information for the requested topic and prepares a short research report.
2. **Blog writer** uses the research result to draft a readable blog post.
3. The final blog is written to `new-blog-post.md` in the project directory.

The YouTube search tool is configured with the channel URL in `tools.py`. The topic is currently set in `crew.py`.
YouTube search embeddings use Chroma's local ONNX model, so no OpenAI API key is needed.

## Requirements

- Python 3.12 (recommended for this project's current dependencies)

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
```

### 3. Install dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure Groq

Copy `.env.example` to `.env` and set the API key you generated in the [Groq Console](https://console.groq.com/keys):

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=groq/qwen/qwen3.8-27b
```

Keep your real key private. `.env` is ignored by Git; do not commit it or paste the key into source code. The model name can be changed in `.env` if Groq changes availability. The code uses `groq/qwen/qwen3.8-27b` when `GROQ_MODEL_NAME` is not set.

### 5. Run the crew

From the project directory, with the virtual environment active:

```bash
python crew.py
```

The agents run in sequence. When execution completes, check `new-blog-post.md` for the generated post. A later run writes to the same output path.

## Customize the Run

- **YouTube channel:** change `youtube_channel_handle` in `tools.py` to the channel handle to search.
- **Topic:** change the `topic` value passed to `crew.kickoff()` in `crew.py`.
- **Output filename:** change `output_file` on `write_task` in `tasks.py`.
- **Model:** set `GROQ_MODEL_NAME` in `.env` to a model identifier supported by Groq.

The current search is channel-based. Supporting an uploaded/local video or selecting an arbitrary video URL requires changing the YouTube tool and the task input flow.

## Project Structure

| File | Purpose |
| --- | --- |
| `agents.py` | Defines the researcher and writer agents and their Groq LLM. |
| `tasks.py` | Defines the research and writing tasks; writes the blog to Markdown. |
| `tools.py` | Configures the YouTube channel search tool. |
| `crew.py` | Assembles and runs the sequential crew with the topic input. |
| `requirements.txt` | Python dependencies installed into `.venv`. |
| `.env.example` | Template for Groq configuration; copy to `.env`. |

## Troubleshooting

- **`GROQ_API_KEY must be set`:** confirm `.env` exists in the project directory and contains a valid `GROQ_API_KEY` entry. Restart the run after editing it.
- **Authentication or model error:** verify the key in the Groq Console and confirm `GROQ_MODEL_NAME` is currently available to your account.
- **Rate limit or quota error:** wait for the limit to reset, reduce repeated runs, or check your Groq account's current usage limits.
- **No relevant video found:** check the channel handle in `tools.py`, the topic spelling in `crew.py`, and that the channel has matching videos accessible to the search tool.
- **`regex` or `tiktoken` build errors:** use Python 3.12 and create a fresh environment named `.venv312` as shown above. The failed install used Python 3.14; changing the Python version does not change an environment that was already created.
- **Import errors:** activate `.venv312` and install dependencies with `python -m pip install -r requirements.txt` from the project directory.

## Security

Never commit `.env` or expose your Groq API key in logs, screenshots, source code, or public issue reports. If a key is exposed, revoke it in the Groq Console and create a replacement.
