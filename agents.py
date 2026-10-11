from dotenv import load_dotenv
load_dotenv()

import os

from crewai import Agent, LLM

class GroqLLM(LLM):
    def _format_messages_for_provider(self, messages):
        messages = [
            {key: value for key, value in message.items() if key != "cache_breakpoint"}
            for message in messages
        ]
        return super()._format_messages_for_provider(messages)

groq_api_key = os.getenv("GROQ_API_KEY")
groq_model_name = os.getenv("GROQ_MODEL_NAME")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY must be set in the environment or .env file")
if not groq_model_name:
    raise ValueError("GROQ_MODEL_NAME must be set in the environment or .env file")

llm = GroqLLM(
    model=groq_model_name,
    api_key=groq_api_key,
)

def create_agents(yt_tool):
    blog_researcher = Agent(
        role="Blog Researcher from YouTube Videos",
        goal="Find and research the YouTube lecture matching {topic} in the provided channel.",
        verbose=True,
        memory=True,
        backstory=(
            "You research AI, data science, machine learning, and generative AI "
            "lectures and accurately identify their key ideas."
        ),
        tools=[yt_tool],
        llm=llm,
        allow_delegation=True,
    )

    blog_writer = Agent(
        role="Blog Writer",
        goal="Write a compelling, accurate blog post based on the research for {topic}.",
        verbose=True,
        memory=True,
        backstory=(
            "With a flair for simplifying complex topics, you craft engaging "
            "narratives that make discoveries accessible."
        ),
        tools=[yt_tool],
        llm=llm,
        allow_delegation=False,
    )

    return blog_researcher, blog_writer