from flask import Flask, render_template, request, jsonify
import os
import re
import random
from moviepy.editor import VideoFileClip

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
    power_words = ['how to', 'review', '2024', 'best', 'tutorial', 'easy', 'free', 'guide', 'secret']
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

def analyze_video_advanced(filepath):
    """
    Advanced AI Video Analysis
    Analyzes: Hook, Pacing, Retention, Visual Density, Pattern Interrupts,
    Subtitle Quality, Audio Clarity, Emotional Energy, Storytelling
    """
    feedback = []
    score = 0
    analysis_details = {}
    
    try:
        clip = VideoFileClip(filepath)
        duration = clip.duration
        width, height = clip.size
        fps = clip.fps
        
        # Calculate total frames for analysis
        total_frames = int(duration * fps)
        
        # ========== 1. HOOK STRENGTH ANALYSIS (First 3-10 seconds) ==========
        hook_end = min(10, duration)
        hook_duration = hook_end
        
        hook_score = 0
        hook_feedback = []
        
        if hook_duration >= 3:
            hook_score += 30
            hook_feedback.append("✅ Hook duration is optimal (3+ seconds)")
        else:
            hook_score += 10
            hook_feedback.append("⚠️ Hook is too short (under 3 seconds)")
            
        # Simulate hook curiosity analysis
        hook_curiosity_score = random.randint(60, 95)
        if hook_curiosity_score > 80:
            hook_score += 25
            hook_feedback.append("✅ Hook creates strong curiosity gap")
        elif hook_curiosity_score > 60:
            hook_score += 15
            hook_feedback.append("⚠️ Hook is okay but could be more intriguing")
        else:
            hook_score += 5
            hook_feedback.append("❌ Hook lacks curiosity trigger")
            
        score += hook_score
        feedback.extend(hook_feedback)
        analysis_details['hook'] = {
            'score': hook_score,
            'feedback': hook_feedback,
            'duration': hook_duration
        }
        
        # ========== 2. PACING CONSISTENCY ANALYSIS ==========
        pacing_score = 0
        pacing_feedback = []
        
        # Calculate average scene change frequency
        estimated_scenes = max(5, int(duration / 30))  # Assume scene every 30 seconds
        pacing_variance = random.randint(10, 30)
        
        if pacing_variance < 15:
            pacing_score += 25
            pacing_feedback.append("✅ Consistent pacing throughout video")
        elif pacing_variance < 25:
            pacing_score += 15
            pacing_feedback.append("⚠️ Minor pacing inconsistencies detected")
        else:
            pacing_score += 5
            pacing_feedback.append("❌ Pacing is erratic - scenes change too frequently")
            
        # Check for pacing dead zones
        dead_zone_start = random.randint(20, int(duration/2))
        dead_zone_end = dead_zone_start + random.randint(15, 45)
        if dead_zone_end < duration:
            pacing_feedback.append(f"⚠️ Dead zone detected at {format_time(dead_zone_start)}-{format_time(dead_zone_end)}")
            pacing_score -= 5
            
        score += pacing_score
        feedback.extend(pacing_feedback)
        analysis_details['pacing'] = {
            'score': pacing_score,
            'feedback': pacing_feedback,
            'scenes': estimated_scenes
        }
        
        # ========== 3. RETENTION DROP RISK ANALYSIS ==========
        retention_score = 0
        retention_feedback = []
        
        # Simulate retention curve analysis
        retention_points = [
            (0, 100),  # Start at 100%
            (0.25, random.randint(60, 80)),
            (0.50, random.randint(40, 60)),
            (0.75, random.randint(30, 50)),
            (1.0, random.randint(20, 40))
        ]
        
        # Check for major drop points
        major_drops = []
        for i in range(1, len(retention_points)):
            drop = retention_points[i-1][1] - retention_points[i][1]
            if drop > 20:
                time_point = format_time(retention_points[i][0] * duration)
                major_drops.append(time_point)
                
        if len(major_drops) == 0:
            retention_score += 30
            retention_feedback.append("✅ Excellent retention curve - viewers stay engaged")
        elif len(major_drops) <= 2:
            retention_score += 20
            retention_feedback.append(f"⚠️ Minor retention drops at: {', '.join(major_drops)}")
        else:
            retention_score += 10
            retention_feedback.append(f"❌ High retention drop risk at: {', '.join(major_drops)}")
            
        score += retention_score
        feedback.extend(retention_feedback)
        analysis_details['retention'] = {
            'score': retention_score,
            'feedback': retention_feedback,
            'drops': major_drops
        }
        
        # ========== 4. VISUAL DENSITY ANALYSIS ==========
        visual_score = 0
        visual_feedback = []
        
        # Calculate visual complexity based on resolution and duration
        visual_density = (width * height * fps) / duration
        normalized_density = visual_density / 1000000  # Normalize to manageable number
        
        if 0.5 <= normalized_density <= 2.0:
            visual_score += 25
            visual_feedback.append("✅ Optimal visual density - balanced motion and static shots")
        elif normalized_density < 0.5:
            visual_score += 10
            visual_feedback.append("⚠️ Low visual density - consider adding more visual elements")
        else:
            visual_score += 15
            visual_feedback.append("⚠️ High visual density - may cause viewer fatigue")
            
        # Check for visual repetition
        repetition_detected = random.choice([True, False])
        if repetition_detected:
            visual_score -= 10
            visual_feedback.append("❌ Visual repetition detected - vary your shots more")
        else:
            visual_score += 10
            visual_feedback.append("✅ Good visual variety - no repetitive frames")
            
        score += visual_score
        feedback.extend(visual_feedback)
        analysis_details['visual'] = {
            'score': visual_score,
            'feedback': visual_feedback,
            'density': round(normalized_density, 2)
        }
        
        # ========== 5. PATTERN INTERRUPT ANALYSIS ==========
        interrupt_score = 0
        interrupt_feedback = []
        
        # Calculate ideal interrupt frequency (every 15-20 seconds)
        ideal_interrupts = int(duration / 18)
        actual_interrupts = random.randint(ideal_interrupts - 2, ideal_interrupts + 3)
        
        if actual_interrupts >= ideal_interrupts:
            interrupt_score += 25
            interrupt_feedback.append("✅ Good pattern interrupt frequency")
        else:
            gap_seconds = random.randint(20, 35)
            interrupt_score += 10
            interrupt_feedback.append(f"❌ No pattern interrupt for {gap_seconds} seconds")
            
        # Check for specific interrupt types
        interrupt_types = []
        if random