import streamlit as st
import uuid
from src.core.workflow import compile_graph

st.set_page_config(
    page_title="ContentAlchemy",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_state" not in st.session_state:
    st.session_state.last_state = {}
if "graph" not in st.session_state:
    st.session_state.graph = compile_graph()

graph = st.session_state.graph
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚗️ ContentAlchemy")
    st.caption("AI Content Marketing Assistant")
    st.divider()

    st.subheader("Quick prompts")
    examples = [
        "Research the latest trends in AI marketing tools",
        "Write a blog post about sustainable fashion in 2025",
        "Create a LinkedIn post about remote work productivity",
        "Generate an image for a tech startup landing page",
        "Research + write blog + LinkedIn post about generative AI in healthcare",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex[:20]):
            st.session_state.pending_query = ex

    st.divider()
    if st.button("🔄 New conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_state = {}
        st.session_state.graph = compile_graph()
        st.rerun()

# ── Main tabs ────────────────────────────────────────────────────
tab_chat, tab_blog, tab_linkedin, tab_image, tab_research = st.tabs([
    "💬 Chat", "📝 Blog Post", "💼 LinkedIn", "🖼️ Image", "🔍 Research"
])

# ── Chat tab ─────────────────────────────────────────────────────
with tab_chat:
    st.subheader("Chat with ContentAlchemy")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    query = st.chat_input("Ask me to research, write a blog, LinkedIn post, or generate an image...")

    # Handle sidebar quick-prompt injection
    if "pending_query" in st.session_state:
        query = st.session_state.pop("pending_query")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Working on it..."):
                try:
                    result = graph.invoke(
                        {"query": query, "messages": [], "errors": []},
                        config=config,
                    )
                    st.session_state.last_state = result

                    intent = result.get("intent", "research")
                    parts = []

                    if result.get("research_report"):
                        parts.append(f"**Research complete** — I found relevant information and synthesised it into a report.")

                    if result.get("blog_post", {}).get("title"):
                        blog = result["blog_post"]
                        parts.append(f"**Blog post created:** *{blog['title']}*\n"
                                     f"- {blog.get('word_count', '?')} words\n"
                                     f"- Meta: {blog.get('meta_description', '')[:80]}...\n"
                                     f"- Keywords: {', '.join(blog.get('keywords', [])[:3])}")

                    if result.get("linkedin_post", {}).get("content"):
                        lp = result["linkedin_post"]
                        parts.append(f"**LinkedIn post created** — {lp.get('char_count', '?')} characters, "
                                     f"{len(lp.get('hashtags', []))} hashtags")

                    if result.get("image_result", {}).get("url"):
                        parts.append("**Image generated** — see the Image tab to view and download it.")

                    if result.get("errors"):
                        parts.append(f"⚠️ Some issues: {'; '.join(result['errors'][:2])}")

                    response = "\n\n".join(parts) if parts else "Done! Check the tabs above for your content."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    err = f"Something went wrong: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})

# ── Blog tab ─────────────────────────────────────────────────────
with tab_blog:
    blog = st.session_state.last_state.get("blog_post", {})
    if not blog or not blog.get("title"):
        st.info("Ask for a blog post in the Chat tab — it will appear here.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Word count", blog.get("word_count", "—"))
        col2.metric("Keyword density", f"{blog.get('keyword_density', 0)}%")
        col3.metric("Meta chars", blog.get("meta_char_count", "—"))

        st.divider()
        st.subheader(blog["title"])
        st.caption(f"**Meta:** {blog.get('meta_description', '')}")
        st.caption(f"**Keywords:** {', '.join(blog.get('keywords', []))}")
        st.divider()

        edited = st.text_area("Edit blog post", value=blog.get("content", ""), height=500)

        col_md, col_html, col_txt = st.columns(3)
        with col_md:
            st.download_button("⬇️ Markdown", edited, file_name="blog_post.md", mime="text/markdown")
        with col_html:
            import markdown as md_lib
            html_content = md_lib.markdown(edited)
            st.download_button("⬇️ HTML", html_content, file_name="blog_post.html", mime="text/html")
        with col_txt:
            import re
            plain = re.sub(r'#+\s*', '', edited)
            st.download_button("⬇️ Plain text", plain, file_name="blog_post.txt", mime="text/plain")

# ── LinkedIn tab ─────────────────────────────────────────────────
with tab_linkedin:
    lp = st.session_state.last_state.get("linkedin_post", {})
    if not lp or not lp.get("content"):
        st.info("Ask for a LinkedIn post in the Chat tab — it will appear here.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Character count", lp.get("char_count", "—"))
        col2.metric("Hashtags", len(lp.get("hashtags", [])))

        st.divider()
        edited_lp = st.text_area("Edit LinkedIn post", value=lp.get("content", ""), height=300)
        st.markdown("**Hashtags:** " + " ".join(lp.get("hashtags", [])))
        st.download_button("⬇️ Copy as text", edited_lp, file_name="linkedin_post.txt", mime="text/plain")

# ── Image tab ────────────────────────────────────────────────────
with tab_image:
    img = st.session_state.last_state.get("image_result", {})
    if not img or not img.get("url"):
        st.info("Ask for an image in the Chat tab — it will appear here.")
    else:
        st.image(img["url"], use_container_width=True)
        st.caption(f"**Prompt used:** {img.get('prompt_used', '')}")
        st.caption(f"**Model:** {img.get('model_used', '')}")
        if img.get("local_path"):
            with open(img["local_path"], "rb") as f:
                st.download_button("⬇️ Download PNG", f, file_name="generated_image.png", mime="image/png")

# ── Research tab ─────────────────────────────────────────────────
with tab_research:
    report = st.session_state.last_state.get("research_report", "")
    raw_results = st.session_state.last_state.get("research_results", {})

    if not report:
        st.info("Research results will appear here after your first query.")
    else:
        st.subheader("Research Report")
        st.markdown(report)

        if raw_results.get("serp_results"):
            st.divider()
            st.subheader("Sources")
            for r in raw_results["serp_results"]:
                st.markdown(f"**{r['title']}**\n{r['snippet']}\n[{r['link']}]({r['link']})")
                st.divider()
