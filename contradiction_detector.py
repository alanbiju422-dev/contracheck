from transformers import pipeline

# Load the Natural Language Inference (NLI) model.
# 'roberta-large-mnli' is a powerful AI model that checks if two statements 
# contradict each other, support (entail) each other, or are neutral.
MODEL_NAME = "roberta-large-mnli"

# We use the 'text-classification' pipeline for this task.
nli_pipeline = pipeline("text-classification", model=MODEL_NAME)

def detect_contradiction(sentence_a: str, sentence_b: str) -> dict:
    """
    Compares two sentences to determine their logical relationship.
    
    Args:
        sentence_a (str): The first sentence (premise).
        sentence_b (str): The second sentence (hypothesis).
        
    Returns:
        dict: A dictionary containing the lowercase label ("contradiction", 
              "entailment", or "neutral") and the confidence score.
    """
    # The pipeline can accept a dictionary containing 'text' and 'text_pair'
    # to compare the two sentences.
    result = nli_pipeline({"text": sentence_a, "text_pair": sentence_b})
    
    # The pipeline returns a list with one dictionary result, for example:
    # [{'label': 'CONTRADICTION', 'score': 0.999}]
    prediction = result if isinstance(result, dict) else result[0]
    
    # Convert label to lowercase (e.g., 'CONTRADICTION' -> 'contradiction')
    label = prediction['label'].lower()
    score = float(prediction['score'])
    
    return {
        "label": label,
        "score": score
    }

if __name__ == "__main__":
    # Test sentences as requested
    sentence_a = "No previous experience is required."
    sentence_b = "Applicants must have five years of professional experience."
    
    print("Analyzing sentences for contradictions...\n")
    print(f"Sentence A: {sentence_a}")
    print(f"Sentence B: {sentence_b}\n")
    
    # Run the detection function
    result = detect_contradiction(sentence_a, sentence_b)
    
    print("Result:")
    print(f"Label: {result['label']}")
    print(f"Score: {result['score']:.4f}")
