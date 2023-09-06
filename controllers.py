from nlp_utils import get_relevant_info
import os
import openai

class ManualController:
    def __init__(self, model):
        self.model = model

    def handle_query(self, query):
        self.model.add_to_chat_history(query)
        entities = get_relevant_info(query)
        print(f"Extracted entities: {entities}")
        
        key, content = self.model.search_manual(entities, query)
        
        if key:
            page_num = content.count(query)
            return f"Found in manual {key} on page {page_num}. Content: {content}", key
        else:
            gpt_response = self.get_gpt_response(query)
            return gpt_response, None

    def get_gpt_response(self, query):
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY_GPT4')
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "I am Calvin, a test equipment expert..."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error with GPT-4: {str(e)}")
            openai.api_key = os.getenv('OPENAI_API_KEY_GPT35')
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "I am Calvin, a test equipment expert..."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message['content'].strip()

