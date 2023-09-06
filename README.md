# calvin

###V1

to run application you must have docker, python, pip, tesseract for ocr from https://github.com/UB-Mannheim/tesseract/wiki

first create an .env file with api key with variables OPENAI_API_KEY_GPT35="key"  
then in terminal run  
`docker run --name redis -d -p 6379:6379 redis:6.0` 
this will start our container  
then we start our virtual env  
`python -m venv ./venv`  
start our virtual env  
`source venv/bin/activate`  
install our dependencies  
`pip install -r requirements.txt`  
run application  
`python app.py`  
here you should be able to go to localhost:5000 and see a chat interface.  
