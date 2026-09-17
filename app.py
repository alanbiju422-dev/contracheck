import streamlit as st
from contra_engine import analyze_text
from url_checker import check_url
from image_processor import analyze_image
from video_detector import analyze_video
from PIL import Image

# PAGE CONFIGURATION
st.set_page_config(
    page_title="ContraCheck",
    page_icon="🔍",
    layout="wide"
)

# HEADER
st.title("CONTRACHECK")
st.subheader("Find What Humans Might Overlook")
st.write("AI-powered detection of hidden contradictions and inconsistencies in information.")
st.write("---")

tab1, tab2, tab3, tab4 = st.tabs(["TEXT", "URL", "IMAGE", "VIDEO"])

with tab1:
    # OPTIONAL TEXT FILE UPLOAD
    uploaded_file = st.file_uploader("Upload a text document (.txt)", type=["txt"])

    st.write("---")

    # TEXT INPUT
    text_input = st.text_area(
        label="Or paste your text below",
        placeholder="Enter or paste your text here...",
        value="",
        height=350
    )

    # Determine the final text to analyze dynamically
    user_text = ""
    if uploaded_file is not None:
        # Read and decode the uploaded file contents
        user_text = uploaded_file.getvalue().decode("utf-8")
    elif text_input and len(text_input.strip()) > 0:
        # Fall back to the text area input
        user_text = text_input

    # ANALYZE BUTTON
    if st.button("🔍 Analyze Text"):
        # Check if text is empty and warn if so
        if not user_text or len(user_text.strip()) == 0:
            st.warning("⚠️ Please upload a .txt file or paste some text to analyze.")
        else:
            with st.spinner("Analyzing text for hidden contradictions..."):
                try:
                    # 3. Call backend engine dynamically using the actual user-provided text
                    result = analyze_text(user_text)
                    
                    st.write("---")
                    
                    # RESULT SECTION
                    st.header("🔍 ContraCheck Analysis")
                    
                    # Display metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Consistency Score", f"{result['consistency_score']}/100")
                    col2.metric("Total Sentences", result["total_sentences"])
                    col3.metric("Related Pairs Checked", result["related_pairs_checked"])
                    col4.metric("Hidden Inconsistencies Found", result["contradiction_count"])
                    
                    st.write("---")
                    
                    # NO CONTRADICTION CASE
                    if result["contradiction_count"] == 0:
                        st.success("✅ No significant inconsistencies detected.")
                        st.write("---")
                    
                    # CONTRADICTION RESULTS
                    if result["contradiction_count"] > 0:
                        st.subheader("⚠️ Hidden Inconsistencies Detected")
                        
                        # Display a visually clear card for each contradiction
                        for i, contradiction in enumerate(result["contradictions"], start=1):
                            with st.container():
                                st.markdown(f"#### Hidden Inconsistency #{i}")
                                
                                st.markdown("**Statement A:**")
                                st.info(contradiction["sentence_a"])
                                
                                st.markdown("**Statement B:**")
                                st.warning(contradiction["sentence_b"])
                                
                                st.markdown("**Why this is a problem:**")
                                st.write(contradiction.get("explanation", "These two statements appear to conflict with each other."))
                                
                                st.markdown("**AI Confidence:**")
                                confidence_pct = contradiction["contradiction_score"] * 100
                                st.write(f"{confidence_pct:.2f}%")
                                
                                st.write("---")
    
                except Exception as e:
                    # ERROR HANDLING
                    st.error("❌ An error occurred while analyzing the text.")

with tab2:
    st.header("🔗 URL Analysis")
    url_input = st.text_input("Enter or paste a URL below", placeholder="https://example.com", value="")
    
    if st.button("Analyze URL →"):
        if not url_input or len(url_input.strip()) == 0:
            st.warning("⚠️ Please enter a URL to analyze.")
        else:
            with st.spinner("Analyzing URL..."):
                url_result = check_url(url_input)
                
                st.write("---")
                st.header("🔍 URL Analysis")
                
                if url_result["suspicious"]:
                    st.subheader("🔴 NOT SAFE")
                else:
                    st.subheader("🟢 SAFE")
                
                # Risk Indicators
                st.metric("Risk Indicators", f"{url_result['risk_score']}/100")
                
                st.subheader("Detected Issues:")
                if len(url_result["detected_issues"]) > 0:
                    for issue in url_result["detected_issues"]:
                        st.write(f"- {issue}")
                else:
                    st.write("- None detected")
                    
                st.write("---")
                
                if url_result["suspicious"]:
                    st.warning(url_result["explanation"])
                else:
                    st.success(url_result["explanation"])

with tab3:
    st.header("🖼️ Image Analysis")
    st.write("Upload an image containing text to detect hidden inconsistencies.")
    
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", width=350)
            
            if st.button("Analyze Image →"):
                with st.spinner("Running OCR and analyzing text..."):
                    result = analyze_image(image)
                    
                    if "error" in result:
                        st.error(result["error"])
                    elif not result.get("extracted_text"):
                        st.warning("No readable text was detected in this image.")
                    else:
                        st.write("---")
                        st.subheader("🟡 AI IMAGE DETECTION")
                        st.write("Not available in the current prototype.")
                        
                        st.write("---")
                        st.subheader("📄 Extracted Text")
                        st.text_area("OCR Result", result["extracted_text"], height=150, disabled=True)
                        
                        analysis = result["analysis"]
                        if analysis is None:
                            st.error("Failed to analyze extracted text.")
                        else:
                            st.write("---")
                            st.header("🔍 ContraCheck Analysis")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total Sentences", analysis["total_sentences"])
                            col2.metric("Related Pairs Checked", analysis["related_pairs_checked"])
                            col3.metric("Hidden Inconsistencies Found", analysis["contradiction_count"])
                            
                            st.write("---")
                            
                            if analysis["contradiction_count"] == 0:
                                st.success("No significant inconsistencies detected.")
                            else:
                                for i, contradiction in enumerate(analysis["contradictions"], start=1):
                                    with st.container():
                                        st.markdown(f"#### ⚠️ Hidden Inconsistency #{i}")
                                        
                                        st.markdown("**Statement A:**")
                                        st.info(contradiction["sentence_a"])
                                        
                                        st.markdown("**Statement B:**")
                                        st.warning(contradiction["sentence_b"])
                                        
                                        st.markdown("**Why this is a problem:**")
                                        st.write(contradiction.get("explanation", "These two statements appear to conflict."))
                                        
                                        confidence_pct = contradiction["contradiction_score"] * 100
                                        st.markdown("**AI Confidence:**")
                                        st.write(f"{confidence_pct:.2f}%")
                                        
                                        st.write("---")
        except Exception as e:
            st.error(f"❌ Error processing image: {e}")

with tab4:
    st.header("🎥 Video Deepfake Detection")
    st.write("Upload a video to check sampled frames for signs of AI-generated or manipulated content.")
    
    uploaded_video = st.file_uploader(
        "Upload a video",
        type=["mp4", "mov", "avi", "mkv"]
    )
    
    if uploaded_video is not None:
        st.video(uploaded_video)
        
        if st.button("Analyze Video →"):
            with st.spinner("Sampling frames and running deepfake analysis (this may take a moment)..."):
                result = analyze_video(uploaded_video.getvalue())
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.write("---")
                    st.header("🎥 Video Analysis")
                    
                    is_fake = result["prediction"] == "Likely AI-generated / manipulated"
                    
                    if is_fake:
                        st.markdown(f"<h3 style='color: red;'>Prediction: {result['prediction']}</h3>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h3 style='color: green;'>Prediction: {result['prediction']}</h3>", unsafe_allow_html=True)
                        
                    st.write(f"**Frames Analyzed:** {result['total_frames_analyzed']}")
                    st.write(f"**Frames Classified as Fake:** {result['fake_frames']}")
                    st.write(f"**Frames Classified as Real:** {result['real_frames']}")
                    st.write(f"**Fake Frame Ratio:** {result['fake_frame_ratio'] * 100:.1f}%")
                    st.write(f"**Average Model Confidence (Fake):** {result['average_fake_score'] * 100:.1f}%")
                    
                    st.warning("⚠️ This is an AI-assisted screening result, not proof of authenticity.")
                    
                    if result.get("suspicious_frames"):
                        st.write("---")
                        st.subheader("Suspicious Frames")
                        st.write("Below are up to 3 frames that the model flagged as manipulated:")
                        cols = st.columns(len(result["suspicious_frames"]))
                        for i, frame in enumerate(result["suspicious_frames"]):
                            cols[i].image(frame, use_container_width=True, caption=f"Suspicious Frame #{i+1}")
                            
                    st.write("---")
                    st.caption("ContraCheck uses a pretrained deepfake image classifier on sampled video frames. Results are probabilistic and should not be treated as definitive proof.")

# FOOTER
st.write("---")
st.caption("ContraCheck uses semantic similarity and Natural Language Inference to identify potential inconsistencies. Results should be reviewed by a human.")
