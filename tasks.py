from crewai import Task


def create_tasks(yt_tool, blog_researcher, blog_writer):
    research_task = Task(
        description=(
            "Use the video transcript search tool to research the YouTube lecture "
            "matching '{topic}'. Base the report only on retrieved transcript content. "
            "If the transcript cannot be retrieved, report a retrieval failure; do not "
            "claim the video does not exist or use unrelated videos as evidence."
        ),
        expected_output=(
            "A concise report of the lecture's main ideas, grounded in its transcript, "
            "or a clear statement that transcript retrieval failed."
        ),
        tools=[yt_tool],
        agent=blog_researcher,
    )

    write_task = Task(
        description=(
            "Write a well-structured Markdown blog post based only on the research "
            "report for '{topic}'. If the report says retrieval failed, return that "
            "briefly instead of inventing a blog post."
        ),
        expected_output="An accurate Markdown blog post based on the verified lecture research.",
        context=[research_task],
        agent=blog_writer,
        async_execution=False,
    )
    return research_task, write_task