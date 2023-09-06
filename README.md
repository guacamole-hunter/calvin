# Calvin: Your Calibration & Repair Assistant

Calvin is a state-of-the-art application designed to assist users in finding relevant information from technical manuals. Whether you're looking for calibration instructions, setup procedures, or troubleshooting steps, Calvin is here to help.

## Features

- **Semantic Search**: Calvin understands the context of your questions and finds the most relevant sections from the manuals.
- **Support for Multiple Manuals**: Store and search across multiple manuals from different manufacturers.
- **Intuitive Interface**: A simple and user-friendly web interface to ask questions and get answers.
- **Powered by AI**: Utilizes advanced Natural Language Processing techniques to understand and respond to user queries.

## How It Works

1. **Content Extraction**: Calvin processes PDF manuals, extracting their content for easy searching. It can handle both text-based and image-based PDFs.
2. **Content Indexing**: The extracted content is indexed using TF-IDF Vectorization, allowing for efficient and accurate searching.
3. **Semantic Search**: When a user asks a question, Calvin computes the relevance of each section in the manuals to the query. It then presents the most relevant sections to the user.
4. **AI-Powered Responses**: Calvin uses OpenAI's GPT model to generate human-like responses, making the interaction smooth and intuitive.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Redis server
- Docker
- Tesseract https://github.com/UB-Mannheim/tesseract/wiki

### Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/guacamole-hunter/calvin.git
   cd calvin
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   #install spacy
   python -m spacy download en_core_web_sm
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Start Redis Server**:
   Ensure your Redis server is running. If you're new to Redis, [here's a beginner-friendly guide](https://redis.io/topics/quickstart).
   I am using docker so here's the command
   ```
   docker run --name redis -d -p 6379:6379 redis:6.0
   ```

6. **Run Calvin**:
   ```
   python app.py
   ```

7. Open your web browser and go to `http://127.0.0.1:5000/`. You should see Calvin's interface, ready to assist you!

### Usage

1. **Upload Manuals**: Before asking questions, ensure you've included the relevant manuals in the root folder with correct file structure. Calvin will process and index them for searching.
2. **Ask Away**: Type in your question in the provided text box and hit "Send". Calvin will search through the manuals and provide you with instructions based on the most relevant information.

## Support

If you encounter any issues or have suggestions for improvements, please [open an issue on GitHub](https://github.com/guacamole-hunter/calvin/issues).

## Contributing

We welcome contributions! If you'd like to improve Calvin, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

