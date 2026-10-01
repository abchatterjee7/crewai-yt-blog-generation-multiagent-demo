from crewai import Agent, LLM
from tools import yt_tool

from dotenv import load_dotenv
load_dotenv()

import os

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY must be set in the environment or .env file")

llm = LLM(
    model=os.getenv("GROQ_MODEL_NAME", "groq/llama-3.3-70b-versatile"),
    api_key=groq_api_key,
)

## Create a senior blog content researcher
blog_researcher=Agent(
    role='Blog Researcher from Youtube Videos',
    goal='get the relevant video transcription for the topic {topic} from the provided Yt channel',
    verbose=True,
    memory=True,
    backstory=(
       "Expert in understanding videos in AI Data Science , MAchine Learning And GEN AI and providing suggestion" 
    ),
    tools=[yt_tool],
    llm=llm,
    allow_delegation=True
)

## creating a senior blog writer agent with YT tool
blog_writer=Agent(
    role='Blog Writer',
    goal='Narrate compelling tech stories about the video {topic} from YT video',
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft"
        "engaging narratives that captivate and educate, bringing new"
        "discoveries to light in an accessible manner."
    ),
    tools=[yt_tool],
    llm=llm,
    allow_delegation=False
)
