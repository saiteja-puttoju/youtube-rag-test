import streamlit as st
import re

# Import functions
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



with st.sidebar:
    st.title("🎬 VidNote AI")

    st.markdown('---')
    st.markdown("Transform any YouTube video into key topics, a podcast, or a chatbot.")
    st.markdown("# Input Details")

    youtube_url = st.text_input("Insert YouTube URL: ", placeholder="https://www.youtube.com/watch?v=pBRSZBtirAk")

    
    # --- Language input is REMOVED ---

    page = st.radio("Select the page: ", ['Notes Generator', 'Chat with Video'])

    submit_button = st.button("✨Execute Task", type="secondary")

st.set_page_config(
    page_title = "YouTube AI Assistant",
    layout = "wide",
    page_icon = "▶️",
    menu_items={
    'Get Help': 'https://www.linkedin.com/in/saiteja-puttoju/',
    'About': "LinkedIn Profile: https://www.linkedin.com/in/saiteja-puttoju/"
    }
)

if page == "Notes Generator":
    st.title("🗒 Instant Video Note Generator")
    st.write("> Generate concise notes from any YouTube video using AI.")

elif page == "Chat with Video":
    st.title("🗪 Chat with Video")

if submit_button:
    if not youtube_url:
        st.warning("⚠ Please insert youtube url in sidebar!")
    else:

        video_id = extract_video_id(youtube_url)

        with st.spinner("Step 1/3 : Fetching Video Transcripts..."):
            # --- THIS IS THE NEW LOGIC ---
            transcript_data, lang_code_or_error = get_best_transcript(video_id)

            if not transcript_data:
                # If it failed, show the error and stop
                st.error(f"Failed to get transcript: {lang_code_or_error}")
            else:
                # If it succeeded, set our variables
                lang_code = lang_code_or_error
                
                full_transcript = " ".join([line.text for line in transcript_data])

        if full_transcript:
                
            # We can now check the language code
            if lang_code != 'en':
                with st.spinner("Step 1.5/3 : Translating transcripts into English..."):
                                      
                    full_transcript = translate_text(full_transcript)
        
            if page == "Notes Generator":
                # The rest of your code runs perfectly from here
                with st.spinner("Step 2/3 : Fetching key topics..."):
                    
                    topics = get_important_topics(full_transcript)
                    st.session_state.topic = topics
                    # st.header("Key Topics: ")
                    # st.info(st.session_state.topic)

                with st.spinner("Step 3/3 : Generating Notes..."):
                    
                    notes = generate_notes(full_transcript)
                    st.session_state.note = notes
                    # st.header("Notes: ")
                    # st.write(st.session_state.note)
                
                st.success("✅ Generated notes successfully!")


            if page == "Chat with Video":
                
                with st.spinner("Step 2/3: Creating chunks and vector store...."):
                    chunks = create_chunks(full_transcript)
                    vectorstore = create_vector_store(chunks)
                    st.session_state.vector_store = vectorstore
                st.session_state.messages = []
                
                st.success("Your video is ready to chat! ask your questions in the chat box.")

        else:
            st.info("Error in fetching transcripts, please try again!")

# Display Notes Generator
if page == "Notes Generator" and "note" in st.session_state and "topic" in st.session_state:
    st.header("Key Topics: ")
    st.info(st.session_state.topic)
    st.header("Notes: ")
    st.write(st.session_state.note)


# chatbot session
if page == "Chat with Video" and "vector_store" in st.session_state:

    st.divider()


    # Display chat messages from history
    for messages in st.session_state.get("messages", []):
        with st.chat_message(messages["role"]):
            st.write(messages["content"])


    # user input
    prompt = st.chat_input("Ask your question about the video")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    
        with st.chat_message("assistant"):
            response = rag_answer(prompt, st.session_state.vector_store)        
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
