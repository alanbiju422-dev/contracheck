# ContraCheck AI Detection System

ContraCheck is an AI-powered detection system built with Streamlit, designed to identify hidden contradictions and inconsistencies in information across multiple formats: Text, URLs, Images, and Videos.

## Features

- **Text Analysis**: Paste text or upload a `.txt` file to detect hidden inconsistencies. Uses semantic similarity and Natural Language Inference (NLI) to analyze pairs of statements and find conflicting claims.
- **URL Analysis**: Checks URLs for potential security risks, suspicious indicators, and overall safety.
- **Image Analysis**: Upload images containing text. Uses OCR (Optical Character Recognition) to extract text and runs the contradiction detection engine on the extracted content.
- **Video Deepfake Detection**: Upload a video file to sample frames and analyze them for signs of AI-generated or manipulated content using a pretrained deepfake image classifier.

## Project Structure

- `app.py`: The main Streamlit web application.
- `contra_engine.py`: Core backend engine for natural language analysis and contradiction detection.
- `contradiction_detector.py`: Model logic for checking textual entailment/contradiction.
- `sentence_processor.py`: Utilities for splitting and processing text sentences.
- `url_checker.py`: Logic for analyzing URLs.
- `image_processor.py`: OCR and image text extraction.
- `video_detector.py`: Logic for sampling video frames and classifying them for deepfakes.

## Installation and Setup

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `streamlit`, `Pillow`, and other necessary AI/ML libraries installed based on your environment)*

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Disclaimer

ContraCheck is an AI-assisted screening tool. Its results (such as deepfake probabilities and sentence contradictions) are probabilistic and should always be reviewed by a human. It is not definitive proof of authenticity or falsehood.
