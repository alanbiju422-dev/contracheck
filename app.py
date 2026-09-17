import streamlit as st
from contra_engine import analyze_text
from url_checker import check_url
from image_processor import analyze_image
from video_detector import analyze_video
from PIL import Image

# PAGE CONFIGURATION
st.set_page_config(
    page_title="ContraCheck | AI-Powered Multimodal Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Global Dark Theme Overrides */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }

    /* Cards */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-1r6slb0, .css-1r6slb0, .st-emotion-cache-1y4p8pa {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 1.5rem;
    }

    /* Accent colors for buttons */
    .stButton>button {
        background-color: #0EA5E9;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0284C7;
        color: white;
        transform: translateY(-1px);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #0EA5E9;
        font-weight: 700;
        font-size: 2.2rem;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
    }

    /* Info / Warning / Success Alerts */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }
    .stAlert[data-baseweb="notification"] {
        background-color: #1E293B;
    }
    
    /* Custom Contradiction Card */
    .contradiction-card {
        background-color: #1E293B;
        border: 1px solid #EF4444;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .contradiction-header {
        color: #EF4444;
        font-weight: 700;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .statement-box {
        background-color: #0F172A;
        border-left: 3px solid #3B82F6;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        color: #E2E8F0;
        font-size: 1.05rem;
    }
    .statement-box.b {
        border-left-color: #F59E0B;
    }
    .vs-badge {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: -10px 0;
        z-index: 10;
        position: relative;
    }
    .vs-badge span {
        background: #334155;
        color: #94A3B8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* URL Status Card */
    .url-status {
        text-align: center;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        font-weight: 800;
        font-size: 2.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .url-safe {
        background-color: rgba(16, 185, 129, 0.1);
        border: 2px solid #10B981;
        color: #10B981;
    }
    .url-unsafe {
        background-color: rgba(239, 68, 68, 0.1);
        border: 2px solid #EF4444;
        color: #EF4444;
    }

    </style>
    """, unsafe_allow_html=True)

load_css()

# HEADER / HERO SECTION
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem; padding: 2rem 0;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span style="font-size: 2rem;">🔍</span>
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 0.05em;">CONTRACHECK</h2>
    </div>
    <span style="background-color: rgba(14, 165, 233, 0.15); color: #38BDF8; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border: 1px solid rgba(14, 165, 233, 0.3);">
        AI-POWERED MULTIMODAL DETECTION
    </span>
    <h1 style="font-size: 3.5rem; font-weight: 800; margin: 1.5rem 0 1rem 0; background: -webkit-linear-gradient(#F8FAFC, #94A3B8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Find What Humans Might Miss.
    </h1>
    <p style="color: #94A3B8; font-size: 1.1rem; max-width: 650px; margin: 0 auto; line-height: 1.6;">
        ContraCheck uses AI to detect hidden contradictions, suspicious links, manipulated visuals, and inconsistencies across text, URLs, images, and video.
    </p>
</div>
""", unsafe_allow_html=True)

# TABS NAVIGATION
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 TEXT DETECTOR", 
    "🔗 URL DETECTOR", 
    "🖼️ IMAGE DETECTOR", 
    "🎥 VIDEO DETECTOR"
])

def render_contradiction_card(i, contradiction):
    confidence_pct = contradiction["contradiction_score"] * 100
    st.markdown(f"""
    <div class="contradiction-card">
        <div class="contradiction-header">
            ⚠️ CONTRADICTION DETECTED
        </div>
        <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 0.5rem; text-transform: uppercase; font-weight: 600;">Statement A</div>
        <div class="statement-box">
            {contradiction["sentence_a"]}
        </div>
        
        <div class="vs-badge"><span>VS</span></div>
        
        <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 0.5rem; margin-top: 0.5rem; text-transform: uppercase; font-weight: 600;">Statement B</div>
        <div class="statement-box b">
            {contradiction["sentence_b"]}
        </div>
        
        <div style="margin-top: 1.5rem; background: rgba(0,0,0,0.25); padding: 1.25rem; border-radius: 8px;">
            <div style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.5rem; font-weight: 600;">Why this is a problem</div>
            <div style="color: #E2E8F0; margin-bottom: 1.25rem; font-size: 1rem; line-height: 1.5;">{contradiction.get("explanation", "These two statements appear to conflict with each other.")}</div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">AI Confidence</span>
                <span style="font-weight: 800; color: #EF4444; font-size: 1.2rem;">{confidence_pct:.2f}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- TEXT DETECTOR -----------------
with tab1:
    st.markdown("### Text Analysis")
    st.markdown("<p style='color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>Paste text or upload a document to identify hidden contradictions and semantic inconsistencies.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_file = st.file_uploader("Upload a text document (.txt)", type=["txt"])
    with col2:
        text_input = st.text_area(
            label="Or paste your text below",
            placeholder="Enter or paste your text here...",
            value="",
            height=200,
            label_visibility="collapsed"
        )
    
    user_text = ""
    if uploaded_file is not None:
        user_text = uploaded_file.getvalue().decode("utf-8")
    elif text_input and len(text_input.strip()) > 0:
        user_text = text_input

    st.write("") # Spacer
    if st.button("Analyze Text"):
        if not user_text or len(user_text.strip()) == 0:
            st.warning("⚠️ Please upload a .txt file or paste some text to analyze.")
        else:
            with st.spinner("Analyzing semantic relationships and checking for contradictions..."):
                try:
                    result = analyze_text(user_text)
                    st.write("---")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Consistency Score", f"{result['consistency_score']}/100")
                    c2.metric("Total Sentences", result["total_sentences"])
                    c3.metric("Related Pairs Checked", result["related_pairs_checked"])
                    c4.metric("Contradictions Found", result["contradiction_count"])
                    
                    st.write("---")
                    
                    if result["contradiction_count"] == 0:
                        st.success("✅ **No significant inconsistencies detected.** The text appears highly consistent.")
                    else:
                        st.markdown("### ⚠️ Analysis Results")
                        for i, contradiction in enumerate(result["contradictions"], start=1):
                            render_contradiction_card(i, contradiction)
                except Exception as e:
                    st.error(f"**Analysis Error:** An unexpected issue occurred during text processing.\n\nDetails: {e}")

# ----------------- URL DETECTOR -----------------
with tab2:
    st.markdown("### URL Security Check")
    st.markdown("<p style='color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>Detect suspicious links and potential security risks before opening.</p>", unsafe_allow_html=True)
    
    url_input = st.text_input("Enter a URL", placeholder="https://example.com", label_visibility="collapsed")
    
    st.write("") # Spacer
    if st.button("Analyze URL"):
        if not url_input or len(url_input.strip()) == 0:
            st.warning("⚠️ Please enter a URL to analyze.")
        else:
            with st.spinner("Scanning URL structure and checking domain reputation..."):
                try:
                    url_result = check_url(url_input)
                    st.write("---")
                    
                    if url_result["suspicious"]:
                        st.markdown("<div class='url-status url-unsafe'>🔴 NOT SAFE</div>", unsafe_allow_html=True)
                        st.error(f"**Warning:** {url_result['explanation']}")
                    else:
                        st.markdown("<div class='url-status url-safe'>🟢 SAFE</div>", unsafe_allow_html=True)
                        st.success(f"**Status:** {url_result['explanation']}")
                        
                    st.write("")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.metric("Risk Score", f"{url_result['risk_score']}/100")
                    
                    with c2:
                        st.markdown("<div style='color: #94A3B8; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 0.05em;'>Detected Issues</div>", unsafe_allow_html=True)
                        if len(url_result["detected_issues"]) > 0:
                            for issue in url_result["detected_issues"]:
                                st.markdown(f"""
                                <div style='background: rgba(239, 68, 68, 0.1); border-left: 4px solid #EF4444; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 4px; color: #F8FAFC;'>
                                    ⚠️ {issue}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style='background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 4px; color: #F8FAFC;'>
                                ✅ No critical issues detected.
                            </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"**Analysis Error:** Unable to scan URL.\n\nDetails: {e}")

# ----------------- IMAGE DETECTOR -----------------
with tab3:
    st.markdown("### Image Analysis")
    st.markdown("<p style='color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>Analyze visual authenticity and detect hidden inconsistencies in extracted text.</p>", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload an image (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image Preview", use_container_width=True)
            
            st.write("") # Spacer
            if st.button("Analyze Image"):
                with st.spinner("Analyzing visual authenticity and extracting text (OCR)..."):
                    result = analyze_image(image)
                    
                    if "error" in result:
                        st.error(f"**Analysis Error:** {result['error']}")
                    else:
                        st.write("---")
                        
                        st.markdown("### 👁️ Visual Authenticity")
                        st.info("Visual AI detection model is not available in the current prototype phase. Showing OCR text analysis results below.")
                        
                        st.write("---")
                        st.markdown("### 📄 OCR / Text Analysis")
                        
                        if not result.get("extracted_text"):
                            st.warning("No readable text was detected in this image.")
                        else:
                            with st.expander("View Extracted Text", expanded=False):
                                st.text(result["extracted_text"])
                                
                            analysis = result["analysis"]
                            if analysis is None:
                                st.error("**Analysis Error:** Failed to analyze extracted text.")
                            else:
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Total Sentences", analysis["total_sentences"])
                                c2.metric("Related Pairs", analysis["related_pairs_checked"])
                                c3.metric("Contradictions", analysis["contradiction_count"])
                                
                                st.write("---")
                                if analysis["contradiction_count"] == 0:
                                    st.success("✅ **No significant inconsistencies detected in the extracted text.**")
                                else:
                                    st.markdown("#### ⚠️ Analysis Results")
                                    for i, contradiction in enumerate(analysis["contradictions"], start=1):
                                        render_contradiction_card(i, contradiction)
        except Exception as e:
            st.error(f"**Analysis Error:** Error processing image.\n\nDetails: {e}")

# ----------------- VIDEO DETECTOR -----------------
with tab4:
    st.markdown("### Video Analysis")
    st.markdown("<p style='color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>Analyze sampled video frames for visual authenticity.</p>", unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader(
        "Upload a video (MP4, MOV, AVI)",
        type=["mp4", "mov", "avi", "mkv"]
    )
    
    if uploaded_video is not None:
        video_col1, video_col2, video_col3 = st.columns([1, 2, 1])
        with video_col2:
            st.video(uploaded_video)
        
        st.write("") # Spacer
        if st.button("Analyze Video"):
            with st.spinner("Processing video frames and analyzing visual authenticity..."):
                try:
                    result = analyze_video(uploaded_video.getvalue())
                    
                    if "error" in result:
                        st.error(f"**Analysis Error:** {result['error']}")
                    else:
                        st.write("---")
                        st.markdown("### 🎥 Video Analysis Results")
                        
                        is_fake = result["prediction"] == "Likely AI-generated / manipulated"
                        
                        if is_fake:
                            st.markdown(f"<div class='url-status url-unsafe'>⚠️ {result['prediction'].upper()}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='url-status url-safe'>✅ {result['prediction'].upper()}</div>", unsafe_allow_html=True)
                        
                        st.write("")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Frames Analyzed", result["total_frames_analyzed"])
                        c2.metric("Fake Frame Ratio", f"{result['fake_frame_ratio'] * 100:.1f}%")
                        c3.metric("Model Confidence", f"{result.get('confidence', result.get('average_fake_score', 0)) * 100:.1f}%")
                        
                        st.write("")
                        c4, c5, _ = st.columns(3)
                        c4.metric("Frames (Real)", result["real_frames"])
                        c5.metric("Frames (Fake)", result["fake_frames"])
                        
                        st.write("")
                        st.info("ℹ️ **Analysis is performed on sampled video frames using a pretrained visual classifier.** This is an AI-assisted screening result, not definitive proof of authenticity.")
                        
                        if result.get("suspicious_frames") and len(result["suspicious_frames"]) > 0:
                            st.write("---")
                            st.markdown("#### Suspicious Frames")
                            st.markdown("<p style='color: #94A3B8; font-size: 0.95rem;'>Below are frames that the model flagged as highly likely to be manipulated:</p>", unsafe_allow_html=True)
                            
                            cols = st.columns(len(result["suspicious_frames"]))
                            for i, frame in enumerate(result["suspicious_frames"]):
                                cols[i].image(frame, use_container_width=True, caption=f"Suspicious Frame #{i+1}")
                except Exception as e:
                    st.error(f"**Analysis Error:** Unable to process video.\n\nDetails: {e}")

# FOOTER
st.markdown("""
<div style="text-align: center; margin-top: 5rem; padding-top: 2rem; border-top: 1px solid #1E293B;">
    <div style="font-weight: 800; color: #F8FAFC; margin-bottom: 0.5rem; letter-spacing: 0.05em; font-size: 1.1rem;">CONTRACHECK</div>
    <div style="color: #94A3B8; font-size: 0.9rem; font-style: italic; margin-bottom: 1rem;">"Find What Humans Might Miss."</div>
    <div style="background-color: rgba(14, 165, 233, 0.05); color: #64748B; font-size: 0.8rem; padding: 0.75rem; border-radius: 6px; display: inline-block; border: 1px solid rgba(14, 165, 233, 0.1);">
        AI-assisted screening tool. Results should be independently verified.
    </div>
</div>
""", unsafe_allow_html=True)
