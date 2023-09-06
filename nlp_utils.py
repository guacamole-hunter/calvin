import spacy

nlp = spacy.load("en_core_web_sm")

def get_relevant_info(query):
    doc = nlp(query)
    
    # Extract entities like equipment names, actions (calibrate, repair), etc.
    entities = [ent.text for ent in doc.ents]
    
    # Extract nouns and noun chunks as they might be relevant
    nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]

    # Combine all extracted terms
    terms = list(set(entities + nouns + noun_chunks))
    
    # Print the extracted terms for debugging
    print(f"Extracted terms: {terms}")
    
    return terms

