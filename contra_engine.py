from sentence_processor import find_related_pairs, split_into_sentences
from contradiction_detector import detect_contradiction

def analyze_text(text: str) -> dict:
    """
    Main engine function to analyze text for logical contradictions.
    
    Workflow:
    1. Splits the text and finds semantically related sentence pairs.
    2. Runs NLI (Natural Language Inference) on related pairs.
    3. Filters for highly confident contradictions.
    4. Calculates an overall consistency score.
    """
    # 1. Handle empty or very short input safely
    if not text or not isinstance(text, str) or len(text.strip()) < 5:
        return {
            "total_sentences": 0,
            "related_pairs_checked": 0,
            "contradiction_count": 0,
            "consistency_score": 100,
            "contradictions": []
        }
        
    # Get the total number of sentences for reporting
    sentences = split_into_sentences(text)
    total_sentences = len(sentences)
    
    # 2. Find semantically related sentence pairs using a lower threshold
    # to catch concepts that are related but worded differently
    related_pairs = find_related_pairs(text, similarity_threshold=0.35)
    
    contradictions_found = []
    
    # Track added pairs to avoid duplicates
    added_pairs = set()
    
    def format_for_explanation(s):
        s = s.strip()
        if s.endswith('.'):
            s = s[:-1]
        if s:
            s = s[0].lower() + s[1:]
        return s
    
    # 3. Check each related pair for contradictions in BOTH directions
    for pair in related_pairs:
        sentence_a = pair["sentence_a"]
        sentence_b = pair["sentence_b"]
        
        # Ensure consistent ordering for deduplication
        pair_key = tuple(sorted([sentence_a, sentence_b]))
        if pair_key in added_pairs:
            continue
            
        # Check A -> B
        result_ab = detect_contradiction(sentence_a, sentence_b)
        
        # Check B -> A
        result_ba = detect_contradiction(sentence_b, sentence_a)
        
        is_contradiction_ab = (result_ab["label"] == "contradiction" and result_ab["score"] >= 0.70)
        is_contradiction_ba = (result_ba["label"] == "contradiction" and result_ba["score"] >= 0.70)
        
        if is_contradiction_ab or is_contradiction_ba:
            # 4. Keep the stronger contradiction score
            scores = []
            if is_contradiction_ab: scores.append(result_ab["score"])
            if is_contradiction_ba: scores.append(result_ba["score"])
            best_score = max(scores)
            
            explanation = f"The first statement says that {format_for_explanation(sentence_a)}, while the second statement says that {format_for_explanation(sentence_b)}."
            
            contradictions_found.append({
                "sentence_a": sentence_a,
                "sentence_b": sentence_b,
                "similarity_score": pair["similarity_score"],
                "contradiction_score": best_score,
                "label": "contradiction",
                "explanation": explanation
            })
            added_pairs.add(pair_key)
    # 5. Calculate a simple consistency score
    # Start at 100, subtract 20 points for each strong contradiction found
    penalty = len(contradictions_found) * 20
    consistency_score = max(0, 100 - penalty)
    
    # 6. Return the structured results dictionary
    return {
        "total_sentences": total_sentences,
        "related_pairs_checked": len(related_pairs),
        "contradiction_count": len(contradictions_found),
        "consistency_score": consistency_score,
        "contradictions": contradictions_found
    }

if __name__ == "__main__":
    import sys
    
    # Read text from command line arguments or use a fallback unrelated example
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
    else:
        # Fallback unrelated test (not the job description)
        test_text = (
            "The product description says the bottle contains 1 litre.\n"
            "The specification table states the bottle capacity is 750 ml.\n"
            "The product is available in blue and red."
        )
    
    print("Running ContraCheck Engine Developer Test...\n")
    results = analyze_text(test_text)
    
    print("=== ContraCheck Report ===")
    print(f"Consistency Score:     {results['consistency_score']}/100")
    print(f"Total Sentences:       {results['total_sentences']}")
    print(f"Related Pairs Checked: {results['related_pairs_checked']}")
    print(f"Contradictions Found:  {results['contradiction_count']}\n")
    
    if results['contradiction_count'] > 0:
        print("--- Detected Contradictions ---")
        for i, c in enumerate(results['contradictions'], 1):
            print(f"Pair #{i}:")
            print(f"  Sentence A: {c['sentence_a']}")
            print(f"  Sentence B: {c['sentence_b']}")
            print(f"  Confidence: {c['contradiction_score']:.4f}")
            print(f"  Explanation: {c['explanation']}\n")
