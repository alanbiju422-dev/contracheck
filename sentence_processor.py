import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util

# Load the pretrained Sentence-BERT model.
# The 'all-MiniLM-L6-v2' model is fast and highly efficient for sentence embeddings.
MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

def split_into_sentences(text: str) -> List[str]:
    """
    Cleans the input text and splits it into individual meaningful sentences.
    
    Args:
        text (str): The long text string to process.
        
    Returns:
        List[str]: A list of cleaned sentences.
    """
    # Safely handle empty, None, or very short inputs
    if not text or not isinstance(text, str):
        return []
        
    # Basic cleaning: remove extra whitespace, tabs, and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) < 3:
        return []
        
    # Sentence Processing:
    # We split the text into sentences using a regular expression.
    # This splits on periods, exclamation marks, or question marks followed by a space.
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out any resulting empty or exceptionally short strings
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]
    return sentences

def find_related_pairs(text: str, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Processes text to find pairs of semantically related sentences.
    
    Args:
        text (str): The input text to analyze.
        similarity_threshold (float): The minimum similarity score (0.0 to 1.0) 
                                      required to consider two sentences related.
                                      
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing related sentence pairs
                              and their similarity scores.
    """
    # 1. Clean and split the text into sentences
    sentences = split_into_sentences(text)
    
    # If there are fewer than 2 sentences, we cannot form any pairs
    if len(sentences) < 2:
        return []

    # 2. Embeddings:
    # We generate embeddings for all sentences.
    # Sentence-BERT converts each sentence into a dense vector (a mathematical 
    # representation of the sentence's semantic meaning).
    embeddings = model.encode(sentences, convert_to_tensor=True)
    
    # 3. Cosine Similarity:
    # Calculate the cosine similarity between all pairs of sentence embeddings.
    # Cosine similarity measures the angle between two vectors; a score closer 
    # to 1.0 means the sentences are very similar in meaning.
    cosine_scores = util.cos_sim(embeddings, embeddings)
    
    related_pairs = []
    # Track pairs we've already added so we don't include duplicates (like A-B and B-A)
    added_pairs = set()
    
    # Compare each sentence with every other sentence
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            # Do not compare a sentence with itself
            if i == j:
                continue
                
            # Create a unique key for the pair (sorting ensures A-B is the same as B-A)
            pair_key = tuple(sorted([i, j]))
            
            if pair_key in added_pairs:
                continue
                
            # Extract the similarity score
            score = cosine_scores[i][j].item()
            
            # If the score meets our threshold, record this pair
            if score >= similarity_threshold:
                related_pairs.append({
                    "sentence_a": sentences[i],
                    "sentence_b": sentences[j],
                    "similarity_score": score
                })
                added_pairs.add(pair_key)
                
    # Sort the results by similarity score (highest first) for easier reading
    related_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return related_pairs

# Example usage block: This runs only if the file is executed directly.
if __name__ == "__main__":
    sample_text = (
        "The quick brown fox jumps over the lazy dog. "
        "A fast, dark-colored fox leaps above a sleepy hound. "
        "Apples are a delicious and healthy fruit. "
        "Eating apples is good for your health."
    )
    
    print("Processing sample text...")
    results = find_related_pairs(sample_text, similarity_threshold=0.6)
    
    print(f"\nFound {len(results)} related pairs:")
    for result in results:
        print(f"- Score: {result['similarity_score']:.4f}")
        print(f"  Sentence A: {result['sentence_a']}")
        print(f"  Sentence B: {result['sentence_b']}\n")
