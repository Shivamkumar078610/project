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