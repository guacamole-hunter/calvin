from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import redis
import joblib
from dotenv import load_dotenv
import openai
import re

# Load environment variables from .env file
load_dotenv()

VECTOR_FILE = "vectorizer.pkl"
SIMILARITY_THRESHOLD = 0.143  # Adjust this value based on your needs

NON_INSTRUCTIONAL_KEYWORDS = [
    "copyright", "all rights reserved", "disclaimer", "warranty", 
    "trademark", "acknowledgment", "preface", "introduction", 
    "table of contents", "index", "appendix", "glossary", 
    "revision history", "confidential", "proprietary", "legal notice"
]

RELEVANT_KEYWORDS = ["calibration", "repair", "servicing", "maintenance", "adjustment", "fix","service",
                     "Mhz", "Ghz", "voltage", "VSWR", "proceedure", "service", "potentiometers", "fuse",
                     ]

class ManualModel:
    def __init__(self):
        self.redis_db = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
        self.chat_history = []
        
        # Load the fitted vectorizer
        if os.path.exists(VECTOR_FILE):
            self.vectorizer = joblib.load(VECTOR_FILE)
        else:
            print("Error: Vectorizer not found. Ensure you've processed the PDFs first.")
            self.vectorizer = TfidfVectorizer()


    def chunk_content(self, content):
        """Breaks down content into contextual chunks based on paragraphs."""
        return content.split('\n\n')  # Splitting by two newlines to get paragraphs




    def extract_related_content(self, content, user_question):
        if not isinstance(user_question, str):
            raise ValueError(f"user_question should be a string, but got {type(user_question)}")

        # Use regex to split content into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        related_paragraphs = []

        # Debug: Print first few paragraphs
        # print("First 5 paragraphs:", paragraphs[:5])

        # Convert user question and paragraphs to TF-IDF vectors
        user_vector = self.vectorizer.transform([user_question])
        para_vectors = self.vectorizer.transform(paragraphs)

        # Compute cosine similarity between user's query and each paragraph
        scores = []
        for idx, para_vector in enumerate(para_vectors):
            similarity = cosine_similarity(user_vector, para_vector)[0][0]

            # Boosting score based on relevant keywords
            for keyword in RELEVANT_KEYWORDS:
                if keyword in paragraphs[idx].lower():
                    similarity += 0.15  # Boosting score by 0.05 for each keyword, adjust as needed

            scores.append((similarity, idx))

        # Debug: Print paragraphs that are filtered out
        filtered_out = [paragraphs[score[1]] for score in scores if any(keyword in paragraphs[score[1]].lower() for keyword in NON_INSTRUCTIONAL_KEYWORDS)]
        # print("Filtered out paragraphs due to keywords:", filtered_out)

        # Filter out paragraphs with non-instructional keywords
        scores = [score for score in scores if not any(keyword in paragraphs[score[1]].lower() for keyword in NON_INSTRUCTIONAL_KEYWORDS)]

        # Sort paragraphs by similarity score in descending order
        sorted_scores = sorted(scores, reverse=True, key=lambda x: x[0])

        # Take the top 5 paragraphs
        top_paragraphs = sorted_scores[:10]
        print(top_paragraphs)

        for score, idx in top_paragraphs:
            # Extracting context around the top paragraph
            start_idx = max(0, idx - 1)
            end_idx = min(len(paragraphs), idx + 2)
            related_paragraphs.extend(paragraphs[start_idx:end_idx])

            # Remove duplicates and join the paragraphs
            related_paragraphs = list(dict.fromkeys(related_paragraphs))
            return '\n\n'.join(related_paragraphs)
    
    def search_manual(self, entities, user_question):
        try:
            # Convert user question to TF-IDF vector
            user_vector = self.vectorizer.transform([user_question])

            # Compute cosine similarity between user's query and all manuals
            similarities = {}
            for key in self.redis_db.keys():
                key_str = key.decode('utf-8')
                content = self.redis_db.get(key).decode('utf-8')
                content_vector = self.vectorizer.transform([content])
                similarity = cosine_similarity(user_vector, content_vector)
                similarities[key_str] = similarity[0][0]

            # Get the manual with the highest similarity score
            priority_keyword = max(similarities, key=similarities.get)

            if similarities[priority_keyword] < SIMILARITY_THRESHOLD:
                return None, "Sorry, I couldn't find a highly relevant manual."
            
            content = self.redis_db.get(priority_keyword).decode('utf-8')

            # Extract related content using keywords from user input
            extracted_content = self.extract_related_content(content, user_question)
            # print(extracted_content)
            # Chunk the related content
            content_chunks = self.chunk_content(extracted_content)
            # Rephrase user question using ChatGPT
            rephrased_question = self.get_gpt_rephrased_question(user_question)
            print (type(rephrased_question))

            # Send chunked content to ChatGPT along with the rephrased question
            response = self.process_with_chatgpt(content_chunks, rephrased_question, entities)

            return priority_keyword, response

        except Exception as e:
            print(f"Error searching manual: {e}")
            return None, None


    def get_gpt_rephrased_question(self, question):
        # Use ChatGPT to rephrase the user's question
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY_GPT35')
            model_name = "gpt-3.5-turbo"
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Please rephrase the following question as a technician."},
                    {"role": "user", "content": question}
                ]
            )
            print("Type of response:", type(response))
            print("Response content:", response.choices[0].message['content'].strip())
        except Exception as e:
            print(f"Error with GPT-3.5 while rephrasing get rephrase gpt: {str(e)}")
            model_name = "gpt-3.5-turbo"  # Fallback to GPT-3
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Please rephrase the following question as a technician."},
                    {"role": "user", "content": question}
                ]
            )
        return response.choices[0].message['content'].strip()



    def process_with_chatgpt(self, content_chunks, rephrased_question, entities):
        for chunk in content_chunks:
            response = self.send_to_chatgpt(chunk, rephrased_question)
            if self.is_relevant(response, entities):
                return response
        return "Sorry, I couldn't find relevant information in the manual."



    def send_to_chatgpt(self, chunk, rephrased_question):
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY_GPT35')
            model_name = "gpt-4"
            
            # Check token length and reduce chunk size if necessary
            total_tokens = len(chunk.split()) + len(rephrased_question.split())
            if total_tokens > 4000:  # Keeping a buffer below the 4097 limit
                chunk = ' '.join(chunk.split()[:4000-len(rephrased_question.split())])
            
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "I am Calvin, a test equipment expert. I am speaking with technicians and will give detailed step by step instructions as responses. I will clarify as needed to complete previous task."},
                    {"role": "user", "content": rephrased_question},
                    {"role": "assistant", "content": chunk}
                ]
            )
            print(chunk, rephrased_question)
        except Exception as e:
            print(f"Error with GPT-3.5 send to gpt: {str(e)}")
            model_name = "gpt-3.5-turbo"  # Fallback to GPT-3
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "I am Calvin, a test equipment expert..."},
                    {"role": "user", "content": rephrased_question},
                    {"role": "assistant", "content": chunk}
                ]
            )
        return response.choices[0].message['content'].strip()



    def add_to_chat_history(self, message):
        self.chat_history.append(message)
        print(message)

    def get_chat_context(self):
        return self.chat_history[-5:]



    def is_relevant(self, response, entities):
        # Filter out non-string entities
        entities = [entity for entity in entities if isinstance(entity, str)]
        
        # Check for keyword density
        entity_count = sum([response.lower().count(entity.lower()) for entity in entities])
        if entity_count / len(response.split()) < 0.05:  # Adjust this threshold as needed
            return False
        
        # Filter out very short or very long responses
        if len(response.split()) < 10 or len(response.split()) > 500:  # Adjust these numbers as needed
            return False
        
        # Filter out non-instructional content
        if any(keyword in response.lower() for keyword in NON_INSTRUCTIONAL_KEYWORDS):
            return False
        
        # Regular expression check for instructional content
        instructional_patterns = [r'\d+\.\s', r'^\s*[-\*]', r'\bstep\b', r'\bprocedure\b']  # Added patterns for bullet points, "step", and "procedure"
        if any(re.search(pattern, response) for pattern in instructional_patterns):
            return True
        
        return any(entity in response.lower() for entity in entities)

