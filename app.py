import streamlit as st

st.set_page_config(page_title="Lecture Blog Generator", page_icon="📝", layout="wide")
st.title("Lecture Blog Generator")
st.caption("Choose a YouTube channel and lecture to research and turn into a blog post.")

with st.form("lecture_form"):
    channel = st.text_input(
        "YouTube channel handle or URL",
        placeholder="@channelname or https://www.youtube.com/@channelname",
    )
    lecture_name = st.text_input(
        "Video lecture name",
        placeholder="For example: The Ultimate Guide to API Architectures",
    )
    submitted = st.form_submit_button("Research and write", type="primary")

if submitted:
    normalized_channel = channel.strip()
    normalized_name = lecture_name.strip()
    if not normalized_channel or not normalized_name:
        st.warning("Enter both a YouTube channel and a lecture name.")
    else:
        st.session_state["channel"] = normalized_channel
        st.session_state["lecture_name"] = normalized_name
        st.session_state.pop("crew_result", None)
        try:
            from crew import run_crew

            with st.status("Researching the lecture and writing the blog...", expanded=True) as status:
                st.write("Loading videos from the selected YouTube channel.")
                result = run_crew(normalized_name, normalized_channel)
                st.session_state["crew_result"] = result
                status.update(label="Blog generation complete", state="complete", expanded=False)
        except Exception as error:
            st.error(f"Generation failed: {error}")

result = st.session_state.get("crew_result")
if result is not None:
    st.divider()
    st.subheader("Input")
    st.write(f"Channel: {st.session_state.get('channel', '')}")
    st.write("Lecture:")
    st.write(st.session_state.get("lecture_name", ""))

    st.subheader("Task outputs")
    for index, task_output in enumerate(result.tasks_output, start=1):
        with st.expander(f"Task {index}", expanded=index == 1):
            st.markdown(task_output.raw or "No task output was returned.")

    final_blog = result.raw or "No final blog was returned."
    st.subheader("Final blog")
    st.markdown(final_blog)
    with st.expander("Markdown source"):
        st.code(final_blog, language="markdown")
    st.download_button(
        "Download Markdown",
        data=final_blog,
        file_name="lecture-blog.md",
        mime="text/markdown",
    )
elif st.session_state.get("lecture_name"):
    st.caption(f"Last submitted lecture: {st.session_state['lecture_name']}")
