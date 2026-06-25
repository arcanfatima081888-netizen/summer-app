from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import datetime
import glob
import random
import logging

# ============================================
# LOGGING SETUP
# ============================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# APP CONFIGURATION
# ============================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
app.config['PHOTOS_FOLDER'] = 'photos'
app.config['VIDEOS_FOLDER'] = 'videos'
app.config['GUESTBOOK_FILE'] = 'guestbook/comments.txt'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Allowed extensions
app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['ALLOWED_VIDEO_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

# Create necessary folders
os.makedirs(app.config['PHOTOS_FOLDER'], exist_ok=True)
os.makedirs(app.config['VIDEOS_FOLDER'], exist_ok=True)
os.makedirs('guestbook', exist_ok=True)

# Initialize guestbook file
if not os.path.exists(app.config['GUESTBOOK_FILE']):
    with open(app.config['GUESTBOOK_FILE'], 'w') as f:
        f.write('')

CORS(app)

# ============================================
# CUTE GREETINGS
# ============================================
CUTE_GREETINGS = [
    "🌸 You're so special!",
    "🌈 You make everything brighter!",
    "💖 You're amazing, friend!",
    "🌻 You're like sunshine!",
    "🦋 You're beautiful inside and out!",
    "⭐ You're a star!",
    "🌺 You're wonderful!",
    "💫 You're magical!",
    "✨ You're one of a kind!",
    "🌷 You're truly special!",
]

# ============================================
# SURPRISE MESSAGES - EDIT THESE!
# ============================================
CUTE_MESSAGES = [
    {"emoji": "💕", "title": "You're the best!", "message": "Thank you for being such a special friend!"},
    {"emoji": "🌸", "title": "You're beautiful!", "message": "Inside and out, you're absolutely lovely!"},
    {"emoji": "🌈", "title": "You're my rainbow!", "message": "You make everything colorful and bright!"},
    {"emoji": "🦋", "title": "You're magical!", "message": "You bring so much joy to everyone around you!"},
    {"emoji": "🌻", "title": "You're sunshine!", "message": "You light up every room you walk into!"},
    {"emoji": "💖", "title": "You're wonderful!", "message": "The world is better because you're in it!"},
    {"emoji": "⭐", "title": "You're a star!", "message": "You shine so bright, my special friend!"},
    {"emoji": "🌺", "title": "You're lovely!", "message": "Your kindness and warmth make me smile!"},
    {"emoji": "✨", "title": "You're magical!", "message": "There's no one else quite like you!"},
    {"emoji": "🌷", "title": "You're precious!", "message": "Our friendship means the world to me!"},
    
    # ----- ✨ ADD YOUR PERSONAL MESSAGES HERE ✨ -----
    {"emoji": "🌟", "title": "My Favorite Person!", "message": "You make every day better just by being you!"},
    {"emoji": "🎀", "title": "So Grateful for You!", "message": "I'm so lucky to have you in my life!"},
    {"emoji": "💫", "title": "You're One of a Kind!", "message": "There's nobody else like you!"},
    {"emoji": "🌹", "title": "A True Friend!", "message": "Thank you for always being there for me!"},
    {"emoji": "🎈", "title": "You Make Me Smile!", "message": "Every time I think of you, I smile!"},
    {"emoji": "💎", "title": "You're a Gem!", "message": "Rare, precious, and absolutely beautiful!"},
]

# ============================================
# STATIC FILE SERVING
# ============================================
@app.route('/photos/<filename>')
def serve_photo(filename):
    try:
        return send_from_directory(app.config['PHOTOS_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving photo {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/videos/<filename>')
def serve_video(filename):
    try:
        return send_from_directory(app.config['VIDEOS_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

# ============================================
# TEST ROUTES
# ============================================
@app.route('/test')
def test():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.datetime.now().isoformat(),
        'message': '🌸 Hello, special friend!'
    })

@app.route('/debug/files')
def debug_files():
    photos = []
    videos = []
    
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        photos.extend(glob.glob(os.path.join(app.config['PHOTOS_FOLDER'], ext)))
    
    for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv', '*.webm']:
        videos.extend(glob.glob(os.path.join(app.config['VIDEOS_FOLDER'], ext)))
    
    return jsonify({
        'photos': [os.path.basename(p) for p in photos],
        'videos': [os.path.basename(v) for v in videos],
        'photo_count': len(photos),
        'video_count': len(videos)
    })

# ============================================
# HELPER FUNCTIONS
# ============================================
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_media_files():
    photos = []
    videos = []
    
    try:
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
            for file_path in glob.glob(os.path.join(app.config['PHOTOS_FOLDER'], ext)):
                filename = os.path.basename(file_path)
                photos.append({
                    'filename': filename,
                    'url': url_for('serve_photo', filename=filename)
                })
        
        for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv', '*.webm']:
            for file_path in glob.glob(os.path.join(app.config['VIDEOS_FOLDER'], ext)):
                filename = os.path.basename(file_path)
                videos.append({
                    'filename': filename,
                    'url': url_for('serve_video', filename=filename)
                })
    except Exception as e:
        logger.error(f"Error getting media files: {e}")
    
    return photos, videos

def get_comments():
    comments = []
    try:
        if os.path.exists(app.config['GUESTBOOK_FILE']):
            with open(app.config['GUESTBOOK_FILE'], 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            comments.append({
                                'timestamp': parts[0],
                                'name': parts[1],
                                'message': '|'.join(parts[2:])
                            })
    except Exception as e:
        logger.error(f"Error reading comments: {e}")
    
    return comments

def save_comment(name, message):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        with open(app.config['GUESTBOOK_FILE'], 'a', encoding='utf-8') as f:
            f.write(f"{timestamp}|{name}|{message}\n")
        return True
    except Exception as e:
        logger.error(f"Error saving comment: {e}")
        return False

# ============================================
# RESET FUNCTIONS
# ============================================
def reset_photos():
    try:
        for file in os.listdir(app.config['PHOTOS_FOLDER']):
            file_path = os.path.join(app.config['PHOTOS_FOLDER'], file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error resetting photos: {e}")
        return False

def reset_videos():
    try:
        for file in os.listdir(app.config['VIDEOS_FOLDER']):
            file_path = os.path.join(app.config['VIDEOS_FOLDER'], file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error resetting videos: {e}")
        return False

def reset_comments():
    try:
        with open(app.config['GUESTBOOK_FILE'], 'w') as f:
            f.write('')
        return True
    except Exception as e:
        logger.error(f"Error resetting comments: {e}")
        return False

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def index():
    if not session.get('authenticated', False):
        return redirect(url_for('login'))
    
    photos, videos = get_media_files()
    comments = get_comments()
    
    greeting = random.choice(CUTE_GREETINGS)
    
    return render_template('index.html', 
                         photos=photos, 
                         videos=videos,
                         comments=comments,
                         datetime=datetime,
                         greeting=greeting)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('PASSWORD', 'default_password_123')
        
        if password == correct_password:
            session['authenticated'] = True
            session.permanent = True
            flash('🌸 Welcome, special friend!', 'success')
            return redirect(url_for('index'))
        else:
            flash('💕 Oops! Wrong password. Try again!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('💖 See you soon, special friend!', 'info')
    return redirect(url_for('login'))

# ============================================
# UPLOAD ROUTES
# ============================================

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    file_type = request.form.get('type', 'photo')
    
    try:
        if file_type == 'photo':
            if not allowed_file(file.filename, app.config['ALLOWED_IMAGE_EXTENSIONS']):
                return jsonify({'error': 'Invalid image format'}), 400
            save_folder = app.config['PHOTOS_FOLDER']
        else:
            if not allowed_file(file.filename, app.config['ALLOWED_VIDEO_EXTENSIONS']):
                return jsonify({'error': 'Invalid video format'}), 400
            save_folder = app.config['VIDEOS_FOLDER']
        
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(save_folder, filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Yay! Added to our memories! 💕',
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# GUESTBOOK ROUTES
# ============================================

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    if not name or not message:
        return jsonify({'error': 'Name and message are required'}), 400
    
    if save_comment(name, message):
        return jsonify({'success': True, 'message': 'Your sweet message is saved! 💖'})
    else:
        return jsonify({'error': 'Failed to save comment'}), 500

# ============================================
# RESET ROUTES
# ============================================

@app.route('/reset', methods=['POST'])
def reset_gallery():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        reset_photos()
        reset_videos()
        reset_comments()
        
        logger.info("Gallery reset by admin")
        return jsonify({
            'success': True,
            'message': '🌸 Everything has been refreshed! Time for new memories!'
        })
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return jsonify({'error': 'Failed to reset gallery'}), 500

@app.route('/reset/photos', methods=['POST'])
def reset_photos_only():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if reset_photos():
        return jsonify({
            'success': True,
            'message': '📸 All photos have been cleared!'
        })
    return jsonify({'error': 'Failed to reset photos'}), 500

@app.route('/reset/videos', methods=['POST'])
def reset_videos_only():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if reset_videos():
        return jsonify({
            'success': True,
            'message': '🎥 All videos have been cleared!'
        })
    return jsonify({'error': 'Failed to reset videos'}), 500

@app.route('/reset/comments', methods=['POST'])
def reset_comments_only():
    if not session.get('authenticated', False):
        return jsonify({'error': 'Not authenticated'}), 401
    
    if reset_comments():
        return jsonify({
            'success': True,
            'message': '💬 All messages have been cleared!'
        })
    return jsonify({'error': 'Failed to reset comments'}), 500

# ============================================
# API ROUTES
# ============================================

@app.route('/api/media')
def get_media_api():
    photos, videos = get_media_files()
    return jsonify({
        'photos': photos,
        'videos': videos
    })

@app.route('/surprise')
def surprise():
    return jsonify(random.choice(CUTE_MESSAGES))

@app.route('/cute/greeting')
def cute_greeting():
    return jsonify({'greeting': random.choice(CUTE_GREETINGS)})

# ============================================
# ERROR HANDLING
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)