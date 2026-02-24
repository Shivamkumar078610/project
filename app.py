from flask import Flask, render_template, request, jsonify
import os
import re
from moviepy import VideoFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def analyze_text(data):
    title = data.get('title', '')
    description = data.get('description', '')
    tags = data.get('tags', '')
    
    score = 0
    feedback = []

    # 1. Title Analysis (30 points)
    if 50 <= len(title) <= 60:
        score += 30
        feedback.append("✅ Perfect title length (50-60 chars).")
    elif len(title) > 60:
        score += 15
        feedback.append("⚠️ Title is too long (might get cut off).")
    elif len(title) > 0:
        score += 10
        feedback.append("⚠️ Title is too short.")

    # 2. Description Analysis (30 points)
    word_count = len(description.split())
    if word_count > 150:
        score += 30
        feedback.append("✅ Great detailed description for SEO.")
    elif word_count > 50:
        score += 15
        feedback.append("⚠️ Description is okay, but could be longer.")
    else:
        score += 5
        feedback.append("❌ Description is too short.")

    # 3. Keyword/Tag Analysis (20 points)
    power_words = ['how to', 'review', '2024', 'best', 'tutorial', 'easy', 'free', 'guide']
    tags_lower = tags.lower()
    found_power_words = [word for word in power_words if word in title.lower() or word in tags_lower]
    
    if len(found_power_words) > 0:
        score += 20
        feedback.append(f"✅ Good use of power keywords: {', '.join(found_power_words)}")
    else:
        score += 5
        feedback.append("❌ Add popular keywords like 'Best', 'How to', etc.")

    # 4. Formatting (20 points)
    if len(re.findall(r'[A-Z]', title)) > 3:
        score += 10
        feedback.append("⚠️ Too many capital letters can look like spam.")
    else:
        score += 10
    
    return min(score, 100), feedback

def analyze_video_file(filepath):
    feedback = []
    score = 0
    
    try:
        # Load video metadata
        clip = VideoFileClip(filepath)
        
        # 1. Duration Analysis (30 points)
        duration = clip.duration # in seconds
        if 180 <= duration <= 600: # 3 to 10 minutes is optimal
            score += 30
            feedback.append(f"✅ Perfect duration ({int(duration//60)} min). Great for watch time.")
        elif duration < 60:
            score += 10
            feedback.append(f"⚠️ Video is very short ({int(duration)}s). Might not rank well.")
        else:
            score += 20
            feedback.append(f"✅ Good length ({int(duration//60)} min).")
            
        # 2. Resolution/Quality (30 points)
        width, height = clip.size
        if height >= 1080:
            score += 30
            feedback.append("✅ High Definition (1080p+). YouTube loves HD content.")
        elif height >= 720:
            score += 20
            feedback.append("⚠️ Standard HD (720p). Consider uploading 1080p for better ranking.")
        else:
            score += 5
            feedback.append("❌ Low resolution. This will hurt your click-through rate.")

        # 3. Aspect Ratio (10 points)
        aspect_ratio = width / height
        if 1.7 <= aspect_ratio <= 1.8:
            score += 10
            feedback.append("✅ Perfect 16:9 aspect ratio.")
        else:
            score += 5
            feedback.append("⚠️ Unusual aspect ratio. Resize to 16:9 for best results.")

        # 4. Visual Engagement (Simulated AI) (30 points)
        estimated_cuts = int(duration / 30)
        score += min(estimated_cuts * 2, 30)
        feedback.append(f"🤖 AI Estimate: Detected ~{estimated_cuts} visual segments (Good pacing).")
        
        clip.close()
        
    except Exception as e:
        feedback.append(f"❌ Error analyzing video: {str(e)}")
        
    return min(score, 100), feedback

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get Text Data
    title = request.form.get('title')
    description = request.form.get('description')
    tags = request.form.get('tags')
    
    text_score, text_feedback = analyze_text({
        'title': title, 
        'description': description, 
        'tags': tags
    })
    
    # Handle Video Upload
    video_score = 0
    video_feedback = []
    video_data = None
    
    if 'video' in request.files:
        file = request.files['video']
        if file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            video_score, video_feedback = analyze_video_file(filepath)
            
            # Get duration for display
            clip = VideoFileClip(filepath)
            video_data = {
                "duration": int(clip.duration),
                "resolution": clip.size[1],
                "filename": file.filename
            }
            clip.close()
            
            # Cleanup
            os.remove(filepath)
    
    # Calculate Total Score
    if video_score > 0:
        total_score = (text_score + video_score) // 2
        all_feedback = text_feedback + ["--- VIDEO ANALYSIS ---"] + video_feedback
    else:
        total_score = text_score
        all_feedback = text_feedback
    
    verdict = "Viral Potential" if total_score > 85 else "High Chance" if total_score > 65 else "Average" if total_score > 50 else "Needs Work"

    return jsonify({
        "score": total_score,
        "verdict": verdict,
        "feedback": all_feedback,
        "video_info": video_data
    })

if __name__ == '__main__':
    app.run(debug=True)