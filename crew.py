from crewai import Crew, Process

from agents import blog_researcher, blog_writer
from tasks import create_tasks
from tools import yt_tool

def run_crew(topic: str):
  topic = topic.strip()
  if not topic:
    raise ValueError("Enter a lecture name or topic.")

  research_task, write_task = create_tasks(
    yt_tool, blog_researcher, blog_writer
  )
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