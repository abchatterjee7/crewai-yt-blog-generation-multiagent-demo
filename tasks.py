from crewai import Task


def create_tasks(yt_tool, blog_researcher, blog_writer):
    research_task = Task(
        description=(
            "Find the YouTube lecture titled or covering '{topic}' in the configured "
            "channel. Research its key points and supporting details."
        ),
        expected_output=(
            "A concise, accurate research report about the lecture, including its "
            "main ideas and useful supporting details."
        ),
        tools=[yt_tool],
        agent=blog_researcher,
    )

    write_task = Task(
        description=(
            "Using the research report, write a well-structured blog post about "
            "the YouTube lecture '{topic}'. Do not invent details that are absent "
            "from the research."
        ),
        expected_output="A polished Markdown blog post based on the lecture research.",
        tools=[yt_tool],
        agent=blog_writer,
        async_execution=False,
    )

    return research_task, write_task