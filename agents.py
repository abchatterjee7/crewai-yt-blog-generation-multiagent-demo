from dotenv import load_dotenv
load_dotenv()

import os

from crewai import Agent, LLM

llm = LLM(
    model=os.getenv("GEMINI_MODEL_NAME"),
    api_key=os.getenv("GEMINI_API_KEY")
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