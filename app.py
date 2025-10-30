import streamlit as st
import re # Make sure re is imported

# Import our new, reliable functions
from supporting_functions import (
    extract_video_id,
    get_best_transcript,
    translate_text,
    get_important_topics,
    generate_notes,
    create_chunks,
    create_vector_store,
    rag_answer
)

# --- Sidebar ---
with st.sidebar:
    st.title("🎬 VidNote AI")
    st.markdown('---')
    st.markdown("Transform any YouTube video into key topics, a podcast, or a chatbot.")
    st.markdown("# Input Details")
    youtube_url = st.text_input("Insert YouTube URL: ", placeholder="https://www.youtube.com/watch?v=pBRSZBtirAk")
    
    page = st.radio("Select the page: ", ['Notes Generator', 'Chat with Video'])
    submit_button = st.button("⚡Submit")

# --- Page Config ---
st.set_page_config(
    page_title = "YouTube AI Assistant",
    layout = "wide",
    page_icon = "▶️",
    menu_items={
    'Get Help': 'https.www.linkedin.com/in/saiteja-puttoju/',
    'About': "LinkedIn Profile: https://www.linkedin.com/in/saiteja-puttoju/"
    }
)

# --- Page Titles (runs on every rerun) ---
if page == "Notes Generator":
    st.title("🗒 Instant Video Note Generator")
    st.write("> Generate concise notes from any YouTube video using AI.")

elif page == "Chat with Video":
    st.title("🗪 Chat with Video")

# --- Processing Logic (runs ONLY when button is clicked) ---
if submit_button:
    if not youtube_url:
        st.warning("⚠ Please insert youtube url in sidebar!")
    else:
        video_id = extract_video_id(youtube_url)
        
        if video_id:
            
            # --- START: NEW LOGIC ---
            # Check if this is a new video. If it is, clear all old data.
            if st.session_state.get("current_video_id") != video_id:
                st.session_state.current_video_id = video_id
                # Clear all data from the previous video
                if "topic" in st.session_state:
                    del st.session_state.topic
                if "note" in st.session_state:
                    del st.session_state.note
                if "vector_store" in st.session_state:
                    del st.session_state.vector_store
                if "messages" in st.session_state:
                    del st.session_state.messages
                
                st.info("New video detected. Processing...")
            else:
                st.info("Processing for the same video...")
            # --- END: NEW LOGIC ---
            
            # --- Process only the current page IF it hasn't been processed already ---
            
            if page == "Notes Generator":
                if "note" not in st.session_state:
                    with st.spinner("Step 1/2 : Fetching Transcript..."):
                        transcript_data, lang_code = get_best_transcript(video_id)
                        if transcript_data:
                            full_transcript = " ".join([line['text'] for line in transcript_data])
                            if lang_code != 'en':
                                full_transcript = translate_text(full_transcript)
                            
                            with st.spinner("Step 2/2 : Generating Notes & Topics..."):
                                st.session_state.topic = get_important_topics(full_transcript)
                                st.session_state.note = generate_notes(full_transcript)
                            st.success("✅ Notes generated successfully!")
                        else:
                            st.error(f"Failed to get transcript: {lang_code}")
                else:
                    st.success("✅ Notes already generated for this video.")

            if page == "Chat with Video":
                if "vector_store" not in st.session_state:
                    with st.spinner("Step 1/2 : Fetching Transcript..."):
                        transcript_data, lang_code = get_best_transcript(video_id)
                        if transcript_data:
                            full_transcript = " ".join([line['text'] for line in transcript_data])
                            if lang_code != 'en':
                                full_transcript = translate_text(full_transcript)
                            
                            with st.spinner("Step 2/2 : Creating Vector Store..."):
                                chunks = create_chunks(full_transcript)
                                st.session_state.vector_store = create_vector_store(chunks)
                                st.session_state.messages = [] # Start new chat
                            st.success("✅ Chat is ready for this video!")
                        else:
                            st.error(f"Failed to get transcript: {lang_code}")
                else:
                    st.success("✅ Chat already prepared for this video.")
        else:
            st.error("Could not find a valid YouTube video ID in the URL.")

# --- Display Logic (runs on EVERY rerun) ---

# Display for Notes Generator (if notes exist in session)
if page == "Notes Generator":
    if "note" in st.session_state and "topic" in st.session_state:
        st.header("Key Topics: ")
        st.info(st.session_state.topic)
        st.header("Notes: ")
        st.write(st.session_state.note)
    else:
        st.info("Submit a YouTube URL in the sidebar to generate notes.")

# Display for Chat (if vector store exists in session)
if page == "Chat with Video":
    if "vector_store" in st.session_state:
        # Display the entire chat history
        for message in st.session_state.get("messages", []):
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # User input
        prompt = st.chat_input("Ask your question about the video")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
        
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = rag_answer(prompt, st.session_state.vector_store)        
                    st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Submit a YouTube URL in the sidebar to start chatting.")
