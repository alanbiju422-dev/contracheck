import cv2
import tempfile
import os
import logging
from PIL import Image
from transformers import pipeline

FAKE_FRAME_RATIO_THRESHOLD = 0.50
MAX_ANALYZED_FRAMES = 30

_deepfake_pipeline = None

def get_pipeline():
    global _deepfake_pipeline
    if _deepfake_pipeline is None:
        _deepfake_pipeline = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
    return _deepfake_pipeline

def analyze_video(video_bytes) -> dict:
    fd, temp_video_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    
    try:
        with open(temp_video_path, 'wb') as f:
            f.write(video_bytes)
            
        cap = cv2.VideoCapture(temp_video_path)
        if not cap.isOpened():
            return {"error": "Unable to read this video file."}
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if fps <= 0:
            fps = 30
            
        sample_interval = max(int(fps), 1)
        
        frames_to_analyze = []
        
        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_number % sample_interval == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                frames_to_analyze.append({
                    "frame_number": frame_number,
                    "timestamp": frame_number / fps,
                    "image": img
                })
                
                if len(frames_to_analyze) >= MAX_ANALYZED_FRAMES:
                    break
                    
            frame_number += 1
            
        cap.release()
        
        if not frames_to_analyze:
            return {"error": "No readable video frames were found."}
            
        pipe = get_pipeline()
        
        results = []
        fake_count = 0
        real_count = 0
        total_fake_score = 0.0
        
        suspicious_frames = []
        
        for f in frames_to_analyze:
            prediction = pipe(f["image"])
            
            top_label = prediction[0]['label'].lower()
            
            is_fake = False
            fake_score = 0.0
            
            for p in prediction:
                label_name = p['label'].lower()
                if "fake" in label_name:
                    fake_score = p['score']
                    break
                    
            if "fake" in top_label:
                is_fake = True
                
            if is_fake:
                fake_count += 1
                if len(suspicious_frames) < 3:
                    suspicious_frames.append(f["image"])
            else:
                real_count += 1
                
            total_fake_score += fake_score
            
            results.append({
                "frame_number": f["frame_number"],
                "timestamp": f["timestamp"],
                "is_fake": is_fake,
                "fake_score": fake_score
            })
            
        total_analyzed = len(results)
        fake_ratio = fake_count / total_analyzed
        avg_fake_score = total_fake_score / total_analyzed
        
        prediction_text = "Likely AI-generated / manipulated" if fake_ratio >= FAKE_FRAME_RATIO_THRESHOLD else "Likely Real"
        
        return {
            "total_frames_analyzed": total_analyzed,
            "fake_frames": fake_count,
            "real_frames": real_count,
            "fake_frame_ratio": fake_ratio,
            "average_fake_score": avg_fake_score,
            "prediction": prediction_text,
            "suspicious_frames": suspicious_frames
        }
        
    except Exception as e:
        logging.error(f"Video analysis error: {e}")
        return {"error": f"An error occurred during video analysis: {str(e)}"}
    finally:
        try:
            os.remove(temp_video_path)
        except:
            pass
