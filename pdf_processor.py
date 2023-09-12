import redis
import os
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
import pytesseract
from pdf2image import convert_from_path
import joblib

# Set pytesseract binary path (if required)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Connect to Redis
try:
    # for local use
    #redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
    # when using with docker
    redis_db = redis.StrictRedis(host='redis', port=6379, db=0)
    print("Successfully connected to Redis.")
except redis.ConnectionError:
    print("Error: Unable to connect to Redis.")
    exit()

vectorizer = TfidfVectorizer()
VECTOR_FILE = "vectorizer.pkl"

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf = PdfReader(pdf_file)
        content = ""
        for page in pdf.pages:
            content += page.extract_text()
    return content

def extract_text_from_image(pdf_path):
    images = convert_from_path(pdf_path)
    content = ""
    for image in images:
        content += pytesseract.image_to_string(image)
    return content

# process pdfs
def process_pdfs():
    base_path = "./Manuals"
    all_content = []

    if not os.path.exists(base_path):
        print("Error: The './Manuals' directory does not exist.")
        return

    print("Starting to process PDFs...")

    for manufacturer in os.listdir(base_path):
        print(f"Checking manufacturer: {manufacturer}")
        manufacturer_path = os.path.join(base_path, manufacturer)

        for item in os.listdir(manufacturer_path):
            print(f"Checking item: {item}")
            item_path = os.path.join(manufacturer_path, item)

            if os.path.isdir(item_path):
                for file in os.listdir(item_path):
                    if file.endswith(".pdf"):
                        pdf_path = os.path.join(item_path, file)
                        redis_key = f"{manufacturer}:{item}:{file}"

                        if redis_db.exists(redis_key):
                            print(f"Duplicate detected for {manufacturer} - {item}. Skipping.")
                            continue

                        content = extract_text_from_pdf(pdf_path)
                        if not content:
                            print(f"Attempting OCR processing for {pdf_path}.")
                            content = extract_text_from_image(pdf_path)

                        if content:
                            print("Extracted content snippet:", content[:500])  # Print snippet
                            all_content.append(content)
                            redis_db.set(redis_key, content)
                            # Verify storage
                            retrieved_content = redis_db.get(redis_key).decode('utf-8')
                            print("Retrieved content snippet:", retrieved_content[:500])  # Print snippet
                            print(f"Successfully processed {manufacturer} - {item}.")
                        else:
                            print(f"No content extracted from {pdf_path}. Skipping.")
            else:
                print(f"Skipping {item_path} as it's not a directory.")

    # Check if any content was extracted from the PDFs
    if not all_content:
        print("No content found in any of the PDFs.")
        return

    # Fit the vectorizer on all the content
    vectorizer.fit(all_content)
    joblib.dump(vectorizer, VECTOR_FILE)
    print("Vectorizer fitted on all content and saved to disk.")
    print("Finished processing PDFs.")

if not os.path.exists(VECTOR_FILE):
    process_pdfs()
else:
    vectorizer = joblib.load(VECTOR_FILE)
    print("Loaded vectorizer from disk.")
