import streamlit as st

st.set_page_config(page_title="Lecture Blog Generator", page_icon="📝", layout="wide")
st.title("Lecture Blog Generator")
st.caption("Search the configured YouTube channel and turn a lecture into a blog post.")

with st.form("lecture_form"):
    lecture_name = st.text_input(
        "Video lecture name",
        placeholder="For example: The Ultimate Guide to API Architectures",
    )
    submitted = st.form_submit_button("Research and write", type="primary")

if submitted:
    normalized_name = lecture_name.strip()
    if not normalized_name:
        st.warning("Enter a lecture name to start.")
    else:
        st.session_state["lecture_name"] = normalized_name
        st.session_state.pop("crew_result", None)
        try:
            from crew import run_crew

            with st.status("Researching the lecture and writing the blog...", expanded=True) as status:
                st.write("Searching the configured YouTube channel.")
                result = run_crew(normalized_name)
                st.session_state["crew_result"] = result
                status.update(label="Blog generation complete", state="complete", expanded=False)
        except Exception as error:
            st.error(f"Generation failed: {error}")

result = st.session_state.get("crew_result")
if result is not None:
    st.divider()
    st.subheader("Input")
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
