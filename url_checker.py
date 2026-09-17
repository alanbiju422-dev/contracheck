import socket
import requests
import urllib.parse
import re
import difflib

# Target brands for typosquatting/impersonation checks
TARGET_BRANDS = [
    "paypal", "google", "microsoft", "apple", 
    "amazon", "facebook", "instagram", "netflix"
]

# Suspicious keywords often found in phishing URLs
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", 
    "update", "payment", "banking", "signin", "password"
]

def check_url(url: str) -> dict:
    """
    Analyzes a URL for domain reachability and common phishing indicators.
    """
    url = url.strip()
    # Handle accidental Markdown link formatting: [text](url) -> url
    md_match = re.match(r'^\[.*?\]\((.*?)\)$', url)
    if md_match:
        url = md_match.group(1).strip()
        
    original_url = url
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
        
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""
    full_domain_lower = hostname.lower()
    
    # 1. URL / DOMAIN STATUS
    domain_exists = "Unknown"
    reachable = "Unknown"
    final_url = original_url
    
    if hostname:
        try:
            socket.gethostbyname(hostname)
            domain_exists = True
        except socket.gaierror:
            domain_exists = False
    else:
        domain_exists = False

    if domain_exists:
        try:
            # Check reachability with a fast HEAD request
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code < 400:
                reachable = True
                final_url = response.url
            else:
                # Some servers block HEAD, try GET
                response = requests.get(url, allow_redirects=True, timeout=5, stream=True)
                reachable = response.status_code < 400
                final_url = response.url
        except requests.RequestException:
            reachable = False
    else:
        reachable = False

    # 2. SECURITY / SUSPICIOUSNESS ANALYSIS
    risk_score = 0
    detected_issues = []
    
    # A. HTTPS Check
    if parsed.scheme == "http" or original_url.startswith("http://"):
        detected_issues.append("URL uses unencrypted HTTP instead of HTTPS.")
        risk_score += 10
        
    # B. IP Address Check
    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", full_domain_lower):
        detected_issues.append("Hostname is an IP address, often used to obscure malicious sites.")
        risk_score += 30
        
    # C. Excessive URL length
    if len(url) > 100:
        detected_issues.append("Unusually long URL which might obscure its true destination.")
        risk_score += 10
        
    # D. Excessive subdomains
    parts = full_domain_lower.split('.')
    if len(parts) > 4:
        detected_issues.append(f"Unusually deep subdomain structure ({len(parts)} parts).")
        risk_score += 15
        
    # E. Suspicious characters
    if full_domain_lower.count('-') >= 2:
        detected_issues.append(f"Domain contains {full_domain_lower.count('-')} hyphens, a common phishing pattern.")
        risk_score += 15
        
    if '@' in parsed.netloc:
        detected_issues.append("Contains '@' symbol, which is used to hide the true domain.")
        risk_score += 40
        
    # F. Suspicious keywords in URL
    url_lower = url.lower()
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url_lower]
    if found_keywords:
        detected_issues.append(f"Contains security/action keywords often used in phishing: {', '.join(found_keywords)}.")
        risk_score += 15 * len(found_keywords) # +15 per keyword
        
    # G. Typosquatting / brand impersonation
    is_typosquatting = False
    
    # Split domain by both dots and hyphens to analyze individual words
    domain_words = re.split(r'[-.]', full_domain_lower)
    
    for brand in TARGET_BRANDS:
        # Skip exact domain matches for the brand (e.g., paypal.com)
        if brand + ".com" in full_domain_lower or brand + ".net" in full_domain_lower or brand + ".org" in full_domain_lower:
            # But if it's mixed with suspicious keywords or excessive hyphens, it might still be bad
            if full_domain_lower.count('-') > 0 or len(found_keywords) > 0:
                 detected_issues.append(f"Brand '{brand}' combined with suspicious domain structure/keywords.")
                 risk_score += 30
            continue
            
        # Check against individual words of the domain to find lookalikes
        for word in domain_words:
            if not word or len(word) < 4: 
                continue
                
            if word == brand:
                # Exact match of brand in a subpart (e.g. paypal-login.com)
                detected_issues.append(f"Domain contains exact brand '{brand}' but is not the official brand domain.")
                risk_score += 50
                is_typosquatting = True
                break
            
            # Use difflib to find close matches (typosquatting)
            seq = difflib.SequenceMatcher(None, word, brand)
            ratio = seq.ratio()
            
            if 0.8 <= ratio < 1.0:
                detected_issues.append(f"Domain contains '{word}', a potential typosquatting lookalike for '{brand}'.")
                risk_score += 50
                is_typosquatting = True
                break
        if is_typosquatting:
            break
            
    # Calculate final risk state
    risk_score = min(risk_score, 100)
    suspicious = risk_score >= 40
    
    # H. Output formatting based on reachability and suspiciousness
    if suspicious:
        if domain_exists == True and reachable == True:
            explanation = "⚠️ This domain appears reachable, but the URL contains indicators of possible phishing or brand impersonation."
        elif domain_exists == True and reachable == False:
            explanation = "⚠️ The domain appears to exist, but the website could not be reached during this check. The URL also contains the detected security indicators."
        elif domain_exists == False:
            explanation = "ℹ️ The domain could not be resolved. This does not necessarily mean the URL is malicious."
        else:
            explanation = "ℹ️ The domain status could not be verified."
    else:
        if domain_exists == False:
            explanation = "ℹ️ The domain could not be resolved. This does not necessarily mean the URL is malicious."
        elif domain_exists == "Unknown":
            explanation = "ℹ️ The domain status could not be verified."
        else:
            explanation = "✅ No significant suspicious indicators were detected in the checks performed."
        
    return {
        "url": original_url,
        "domain_exists": domain_exists,
        "reachable": reachable,
        "final_url": final_url,
        "risk_score": risk_score,
        "suspicious": suspicious,
        "detected_issues": detected_issues,
        "explanation": explanation
    }

if __name__ == "__main__":
    import json
    test_urls = [
        "https://paypal.com",
        "http://paypal-secure-login.com/verify-account",
        "https://this-is-a-completely-made-up-domain-for-testing-12345.com"
    ]
    
    for t_url in test_urls:
        print(f"Testing URL: {t_url}")
        res = check_url(t_url)
        print(json.dumps(res, indent=2))
        print("-" * 40)
