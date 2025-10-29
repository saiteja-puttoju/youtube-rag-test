import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import time
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# initialize the gemini model
llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash-lite",
    temperature = 0.2
)


# function to extract video id from youtube url
def extract_video_id(url):
    """
    Extracts the Video ID from given youtube video url
    """

    match = re.search(r"(?:v=|vi=|youtu\.be/|embed/|shorts/|v/)([a-zA-Z0-9_-]{11})", url)

    if match:
        return match.group(1)
    else:
        st.error("Error with youtube Video ID extraction, please check the url once again")
        return None

# --- New Transcript Functions Start ---

def get_best_transcript(video_id: str) -> tuple[list, str] | tuple[None, str]:
    """
    Fetches the best available transcript (any language).
    Prioritizes:
    1. Manual 'en'
    2. Other Manual
    3. Generated 'en'
    4. Other Generated

    Returns:
        A tuple of (transcript_data, language_code)
        or (None, error_message) if it fails.
    """
    
    manual_codes = []
    generated_codes = []
    
    try:
        # 1. Create an instance and get the list object
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id=video_id)
        
        # 2. Sort all available codes into two lists
        for transcript in transcript_list:
            if transcript.is_generated:
                generated_codes.append(transcript.language_code)
            else:
                manual_codes.append(transcript.language_code)
                
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except Exception as e:
        return None, f"Error fetching transcript list: {e}"

    # --- 3. Build the Final Prioritized List ---
    final_priority_list = []

    if 'en' in manual_codes:
        final_priority_list.append('en')
        manual_codes.remove('en')
    
    final_priority_list.extend(manual_codes)

    if 'en' in generated_codes and 'en' not in final_priority_list:
        final_priority_list.append('en')
        generated_codes.remove('en')
    
    final_priority_list.extend(generated_codes)

    # --- 4. Fetch the transcript using the list ---
    if final_priority_list:
        try:
            # Find the best transcript object from our priority list
            transcript_object = transcript_list.find_transcript(final_priority_list)
            
            # Fetch the actual data
            transcript_data = transcript_object.fetch()
            
            # Return the data and its language
            return transcript_data, transcript_object.language_code
            
        except Exception as e:
            return None, f"Could not fetch transcript data: {e}"
    else:
        # No transcripts were found at all
        return None, "No transcripts found for this video."


# function to translate text to English
def translate_text(transcript):
    """
    Translates the given text to the English language.
    """

    try:
        prompt = PromptTemplate.from_template("""
        You are a professional translator.  
        Your task is to translate the following text into English, **preserving all meaning, intent, nuance, tone and style** of the original — without changing or omitting anything.  
        Do **not** add commentary, explanations or interpretations; provide **only** the translation.

        Text to translate:
        '''
        {transcript}
        '''

        Your output should be exactly the translated text in English, and nothing else.
        """)

        chain = prompt | llm

        response = chain.invoke({'transcript': transcript})

        return response.content

    except Exception as e:
        st.error(f"Error with translating: {e}")


# function to get important topics from the transcript
def get_important_topics(transcript):
    """
    Identifies the five most important topics or concepts discussed in the transcript.
    """

    try:
        prompt = PromptTemplate.from_template("""
        You are an expert summarization assistant tasked with analyzing the following video transcript.

        Your assignment:

        - Identify the five most important topics or concepts discussed in the transcript.

        - Each topic should reflect a major theme or idea, not minor details, quotes, or side‐points.

        - Provide the result as a numbered list (1 through 5).

        - Use clear, concise wording focused on the technical content of the video.

        - Do not phrase items as questions or opinions; state them as factual key topics.

        - Only include topics that are actually discussed in the transcript — do not add or infer unrelated ones.

        Transcript:
        '''
        {transcript}
        '''
        """)

        chain = prompt | llm

        response = chain.invoke({"transcript": transcript})

        return response.content

    except Exception as e:
        st.error(f"Error with translating: {e}")


# function to generate notes from the transcript
def generate_notes(transcript):
    """
    Generates concise notes from the transcript, capturing all key points and important information.
    """

    try:
        prompt = PromptTemplate.from_template("""
        You are an expert AI note-taking assistant. Your task is to analyze the following YouTube video transcript and produce clear, well-structured, and concise notes.  

        ⚡ Requirements:  
        - Present the output as **bulleted points**, grouped into logical **sections** with **subheadings**.  
        - Each subheading must begin with a single relevant **emoji**, but **must not include emojis at the end**.  
        ✅ Example: 📌 Childhood Reading Habits  
        ❌ Not allowed: 📌 Childhood Reading Habits 📚  
        - Capture all **key points, important facts, and examples** without adding information not present in the transcript.  
        - Use **short, clear sentences** (avoid long paragraphs, filler, or repetition).  
        - Highlight critical insights with bold labels such as **Key takeaway:**, **Fact:**, or **Example:** where appropriate.  
        - Ensure the notes are easy to scan and suitable for quick review.  

        ✨ Suggested Subheading Styles (emoji at start only):  
        - 📌 Overview  
        - 💡 Key Ideas  
        - 📝 Examples / Case Studies  
        - 🎯 Takeaways  
        - ❓ Questions / Unclear Points  

        Transcript:  
        '''  
        {transcript}  
        '''  
        """)

        chain = prompt | llm

        response = chain.invoke({"transcript": transcript})

        return response.content

    except Exception as e:
        st.error(f"Error with generating notes: {e}")



def create_chunks(transcript):
    """
    Splits the transcript into smaller chunks for processing.
    """

    text_spiltter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    documents = text_spiltter.create_documents([transcript])

    return documents

def create_vector_store(documents):
    """
    Creates a vector store from the given documents using Google Generative AI embeddings.
    """

    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", transport="grpc")
    vector_store = Chroma.from_documents(documents, embedding)

    return vector_store

def rag_answer(question, vectorstore):
    """
    Answers the user's question based on the context from the vector store.
    """

    results = vectorstore.similarity_search(question, k=4)
    context_text = "\n".join([i.page_content for i in results])

    prompt = ChatPromptTemplate.from_template("""
    You are a kind, polite, and precise assistant. 
    Your role is to help the user in a warm, respectful, and professional way.

    Guidelines:
    - Begin with a friendly greeting on the first response (avoid repeating greetings in later turns).
    - Understand the user’s intent even if there are typos or grammar mistakes.
    - Answer strictly based on the retrieved context provided below.
    - If the answer is not in the context, reply with:
      "I couldn’t find that information in the database. Could you please rephrase or ask something else?"
    - Keep answers clear, concise, and approachable.
    - Maintain a helpful and empathetic tone at all times.

    Context:
    {context}

    User Question:
    {question}

    Answer:
    """)

    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})

    return response.content
    
