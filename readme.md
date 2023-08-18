# Multi-Document Reader & Chatbot with Langchain and ChatGPT

## Introduction
------------
The Multi-Document Chat App is a Python application that allows you to chat with multiple documents in different file formats (.pdf, .txt, .docx). You can ask questions about the documents using natural language, and the app will provide relevant responses based on the content of the documents by utilizing a LLM. This app will only respond to questions related to the loaded documents.


## Installation
----------------------------

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. Obtain an API key from OpenAI and add it to the `.env` file in the project directory.
```commandline
OPENAI_API_KEY=your_api_key
```

## Usage
-----
To use the MultiPDF Chat App, follow these steps:

1. Ensure that you have installed the required dependencies and added the OpenAI API key to the `.env` file.

2. Run the `qa_app.py` file using the Streamlit CLI. Execute the following command:
   ```
   streamlit run qa_app.py
   ```

3. The application will launch in your default web browser, displaying the user interface.

4. Load documents into the app by following the provided instructions.

5. Ask questions in natural language about the loaded PDFs using the chat interface.




## License
-------
The MultiPDF Chat App is released under the [MIT License](https://opensource.org/licenses/MIT).