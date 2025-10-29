# 🎬 VidNote AI: AI YouTube Summarizer & Chatbot

VidNote AI is an intelligent web application built with Streamlit that generates concise notes, extracts key topics, and allows you to chat with any YouTube video. It uses the YouTube Transcript API, LangChain, and Google's Gemini AI to create a full-featured RAG (Retrieval-Augmented Generation) pipeline.



---

## 🌟 Key Features

* **Two Modes in One:**
    * **Notes Generator:** Analyzes the video to extract the 5 most important topics and generate a set of detailed, structured notes.
    * **Chat with Video (RAG):** An interactive chat interface that allows you to ask specific questions about the video's content.

* **Automatic Transcript Detection:** Automatically finds the best available transcript for a video. The app prioritizes manual 'en', then other manual languages, then generated 'en', ensuring the highest quality source.

* **Automatic Translation:** Intelligently checks the language code of the fetched transcript. If it's not English, it automatically translates the text before processing.

* **RAG Pipeline:** When "Chat with Video" is selected, the app:
    1.  Chunks the transcript into optimal pieces.
    2.  Creates embeddings using Google's AI models.
    3.  Stores them in a Chroma vector store.
    4.  Uses this vector store to answer user questions with context.

* **Persistent Chat:** Uses Streamlit's `session_state` to store the chat history and the vector store, allowing you to have a continuous conversation without reprocessing the video.

---

## 🛠️ Technologies Used

* **Backend:** Python 3.12
* **Web Framework:** Streamlit
* **AI Model:** Google Gemini (`gemini-2.5-flash-lite`)
* **AI Framework:** LangChain
    * `langchain-google-genai` (for LLM and Embeddings)
    * `langchain-community` (for text splitting)
    * `langchain-chroma` (for the vector store)
* **Vector Store:** ChromaDB
* **Embeddings:** `GoogleGenerativeAIEmbeddings`
* **API/Services:** YouTube Transcript API
* **Dependencies:** `python-dotenv`, `sentence-transformers`

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

* Python 3.12 or later
* A Google API Key with the Gemini API enabled. You can get one from [Google AI Studio](https://makersuite.google.com/).

### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone git clone https://github.com/saiteja-puttoju/ai-youtube-summarizer.git
    cd ai-youtube-assistant
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Linux/macOS
    python -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    * Create a new file in the root of the project named `.env`.
    * Add your Google API key to this file (this is read by `supporting_functions.py`):
      
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```

### Running the Application

Once the setup is complete, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
````

Your web browser will automatically open to the application's user interface.

-----

## How to Use

1.  Open the application in your browser.
2.  On the sidebar, paste the full **YouTube URL** into the text input.
3.  Select your desired mode: **"Notes Generator"** or **"Chat with Video"**.
4.  Click the **"✨Execute Task"** button.

<!-- end list -->

  * **If you selected "Notes Generator":**

      * The app will fetch the transcript, generate key topics, and display the detailed notes on the main page.

  * **If you selected "Chat with Video":**

      * The app will process the video and create a vector store.
      * Once it's ready, a chat box will appear. You can now ask any question about the video's content.
