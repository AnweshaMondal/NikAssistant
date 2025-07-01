import streamlit as st


def render_widgets_panel():
    """Render the widgets panel"""
    st.header("Widgets")

    # Passport Photo Widget
    st.subheader("📷 Passport Photos")
    uploaded_photos = st.file_uploader(
        "Upload Passport Photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )
    if uploaded_photos:
        st.success(f"Uploaded {len(uploaded_photos)} photos")

    # Resume Widget
    st.subheader("📄 Resumes")
    uploaded_resumes = st.file_uploader(
        "Upload Resumes", type=["pdf", "doc", "docx"], accept_multiple_files=True
    )
    if uploaded_resumes:
        st.success(f"Uploaded {len(uploaded_resumes)} resumes")

    # Documents Widget
    st.subheader("📂 Documents")
    uploaded_docs = st.file_uploader(
        "Upload Documents",
        type=["pdf", "doc", "docx", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_docs:
        st.success(f"Uploaded {len(uploaded_docs)} documents")

    # Priority Widget
    st.subheader("⭐ Priority Management")
    priority_items = st.text_area("Add priority items (one per line)")
    if st.button("Save Priorities"):
        priorities = priority_items.split("\n")
        st.success(f"Saved {len(priorities)} priority items")

    st.info("Explore and manage your widgets here!")
