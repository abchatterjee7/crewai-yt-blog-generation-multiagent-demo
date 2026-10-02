from crewai import Crew, Process

from agents import create_agents
from tasks import create_tasks
from tools import create_channel_tool

def run_crew(topic: str, channel: str):
  topic = topic.strip()
  if not topic:
    raise ValueError("Enter a lecture name or topic.")
  if not channel.strip():
    raise ValueError("Enter a YouTube channel handle or URL.")

  yt_tool = create_channel_tool(channel)
  blog_researcher, blog_writer = create_agents(yt_tool)
  research_task, write_task = create_tasks(yt_tool, blog_researcher, blog_writer)
  crew = Crew(
    agents=[blog_researcher, blog_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    memory=True,
    embedder={"provider": "onnx"},
    cache=True,
    max_rpm=100,
    share_crew=True,
  )
  return crew.kickoff(inputs={"topic": topic})