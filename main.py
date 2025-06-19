import os
from flask import Flask, request, jsonify
from openai import OpenAI
from datetime import datetime
import uuid
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Tip: Install python-dotenv to use .env files: pip install python-dotenv")

app = Flask(__name__)

# Add CORS support
try:
    from flask_cors import CORS
    CORS(app, origins="*")  # Allow all origins for development
    print("✅ CORS enabled for all origins")
except ImportError:
    print("Tip: Install flask-cors for better browser support: pip install flask-cors")

try:
    # Try multiple environment variable names for flexibility
    api_key = (os.environ.get('OPENAI_KEY') or 
               os.environ.get('OPENAI_API_KEY') or 
               os.environ.get('OPENAI_TOKEN'))

    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")

    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized successfully")

except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {str(e)}")
    client = None

def create_game_mashup(game1_data, game2_data):
    """The Game Mashup Creator combines two games into something new and exciting."""
    if client is None:
        return "OpenAI client is not initialized. Please check your API key and environment variables."

    prompt = f"""
    You are an expert game designer and creative director. I will give you two different games, and I want you to create an innovative mashup that combines the best elements of both into a completely new game concept.

    **Game 1:**
    {game1_data}

    **Game 2:**
    {game2_data}

    Create a detailed game concept that fuses these two games together. Your response should include:

    ## 🎮 Game Title
    Create an original, catchy title that doesn't use proper nouns from either source game.

    ## 🎯 Genre & Core Concept
    Define the hybrid genre and explain the core fusion concept in 2-3 sentences.

    ## ⚡ Unique Selling Points
    List 3-4 compelling features that make this mashup special and marketable.

    ## 🔄 Core Game Loop
    Describe the primary gameplay cycle that players will experience repeatedly.

    ## 🎨 Key Mechanics Fusion
    Explain how you're combining specific mechanics from both games in creative ways.

    ## 👥 Target Audience
    Identify who would play this game and why it appeals to fans of both source games.

    ## 💰 Monetization Strategy
    Suggest 2-3 ways to make this game profitable while keeping it player-friendly.

    ## 🚀 Marketing Hooks
    Provide 3 compelling marketing angles that would grab attention.

    IMPORTANT: Be creative and innovative. Don't just list features from both games - truly blend them into something new. Use professional language with perfect grammar and formatting.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world-class game designer known for creating innovative game concepts that successfully blend different genres and mechanics. You deliver creative, detailed, and marketable game ideas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85,  # High creativity while maintaining coherence
        max_tokens=2500
    )

    return response.choices[0].message.content

def process_game_mashup(data):
    """Process game mashup request and return results"""
    # Validate required fields
    required_fields = ['mashup_name', 'game1_data', 'game2_data']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f'Missing required field: {field}')

    mashup_name = data['mashup_name']
    game1_data = data['game1_data']
    game2_data = data['game2_data']

    # Generate mashup concept
    print(f"Creating mashup concept: {mashup_name}...")
    mashup_concept = create_game_mashup(game1_data, game2_data)

    # Generate report ID for tracking
    report_id = str(uuid.uuid4())[:8]

    return {
        'success': True,
        'message': 'Game mashup created successfully!',
        'report_id': report_id,
        'mashup_name': mashup_name,
        'concept': mashup_concept,
        'source_games': {
            'game1': game1_data[:100] + "..." if len(game1_data) > 100 else game1_data,
            'game2': game2_data[:100] + "..." if len(game2_data) > 100 else game2_data
        },
        'generated_at': datetime.now().strftime("%B %d, %Y at %I:%M %p")
    }

@app.route('/')
def home():
    """Root endpoint"""
    openai_key = os.environ.get('OPENAI_KEY') or os.environ.get('OPENAI_API_KEY')

    return jsonify({
        'message': 'Game Mashup Creator API is running!',
        'status': 'healthy',
        'endpoints': {
            'health': '/api/health',
            'mashup': '/api/create-mashup (POST)',
            'test': '/api/test (POST)',
            'demo': '/use (GET - Web Interface)'
        },
        'environment_check': {
            'openai_key_set': bool(openai_key),
            'client_ready': bool(client)
        }
    })

@app.route('/api/create-mashup', methods=['POST'])
def api_create_mashup():
    """Main API endpoint for creating game mashups"""
    try:
        data = request.json

        # Check if data is None (no JSON in request)
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        response_data = process_game_mashup(data)
        return jsonify(response_data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error in API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Game Mashup Creator',
        'environment': {
            'openai_configured': bool(client)
        }
    })

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """Test endpoint with sample data"""
    sample_data = {
        'mashup_name': 'TestMash Concept',
        'game1_data': """
        Tetris - A classic puzzle game where players arrange falling geometric blocks (tetrominoes) to complete horizontal lines. The game speeds up as you progress, requiring quick thinking and spatial reasoning. Simple controls, addictive gameplay, and endless replayability have made it one of the most popular games of all time.
        """,
        'game2_data': """
        Dark Souls - A challenging action RPG known for its punishing difficulty, intricate level design, and atmospheric world. Players explore interconnected environments, fight formidable enemies, and learn from repeated deaths. Features stamina-based combat, character progression through souls currency, and environmental storytelling.
        """
    }

    try:
        print("🧪 Running test with sample mashup data...")
        response_data = process_game_mashup(sample_data)
        return jsonify(response_data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error in test endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/use')
def use_page():
    """Serve the mashup HTML page"""
    return r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Mashup Creator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
            font-size: 16px;
        }
        input, textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            box-sizing: border-box;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .games-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        .game-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #e9ecef;
        }
        .game-section h3 {
            margin-top: 0;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .vs-divider {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .vs-divider::before,
        .vs-divider::after {
            content: '';
            height: 2px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            flex: 1;
            margin: 0 20px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 40px;
            border: none;
            border-radius: 12px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin: 20px 0;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .response {
            margin-top: 30px;
            padding: 25px;
            border-radius: 12px;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            border: 2px solid #bee5eb;
        }
        .loading {
            text-align: center;
            padding: 30px;
            color: #667eea;
            font-size: 18px;
        }
        .mashup-result {
            background: #f8f9fa;
            border: 3px solid #667eea;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
        }
        .mashup-result h2 {
            color: #667eea;
            margin-top: 0;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            font-size: 1.8em;
        }
        .mashup-content {
            line-height: 1.7;
            font-size: 16px;
            white-space: pre-wrap;
        }
        .mashup-meta {
            background: #e9ecef;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            font-size: 14px;
            color: #6c757d;
        }
        .intro-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 40px;
        }
        .intro-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            text-align: left;
            margin-top: 25px;
        }
        .feature-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .example-section {
            background: #fff3cd;
            border: 2px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .example-section h4 {
            color: #856404;
            margin-top: 0;
        }
        @media (max-width: 768px) {
            .games-container {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .features-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮⚡ Game Mashup Creator</h1>
        <p class="subtitle">Fuse two games together to create the next gaming sensation!</p>

        <div class="intro-section">
            <h3>🚀 Create Revolutionary Game Concepts</h3>
            <p style="color: #666; font-size: 18px; margin-bottom: 20px;">
                Combine the best elements of any two games to generate innovative, marketable game concepts with AI-powered creativity.
            </p>

            <div class="features-grid">
                <div class="feature-item">
                    <strong>🎯 Smart Fusion</strong><br>
                    <small>Intelligently blends core mechanics from both games</small>
                </div>
                <div class="feature-item">
                    <strong>💡 Original Concepts</strong><br>
                    <small>Creates unique titles and innovative gameplay ideas</small>
                </div>
                <div class="feature-item">
                    <strong>💰 Market Ready</strong><br>
                    <small>Includes monetization and marketing strategies</small>
                </div>
                <div class="feature-item">
                    <strong>🎨 Complete Vision</strong><br>
                    <small>Full game concept with target audience analysis</small>
                </div>
            </div>
        </div>

        <div class="example-section">
            <h4>💡 Example Ideas</h4>
            <p><strong>Tetris + Dark Souls:</strong> "Geometric Purgatory" - A puzzle game where each completed line grants souls to upgrade your block-placement abilities, but mistakes spawn enemies that attack your falling pieces.</p>
            <p><strong>Minecraft + Among Us:</strong> "Impostor Craft" - Build and survive during the day, but at night one player becomes the impostor who can sabotage structures and eliminate others.</p>
        </div>

        <div class="form-group">
            <label for="mashupName">🏷️ Your Mashup Project Name:</label>
            <input type="text" id="mashupName" placeholder="e.g., 'Ultimate Fusion Game', 'Project Nexus', etc." value="">
        </div>

        <div class="games-container">
            <div class="game-section">
                <h3>🎮 Game #1</h3>
                <div class="form-group">
                    <textarea id="game1Data" placeholder="Describe the first game in detail...

Include:
• Genre and core gameplay
• Key mechanics and features  
• Art style and theme
• What makes it unique
• Target platform

Example: 'Tetris - Classic puzzle game where players rotate and arrange falling blocks to clear horizontal lines. Simple controls, increasing difficulty, timeless gameplay...'"></textarea>
                </div>
            </div>

            <div class="game-section">
                <h3>🎮 Game #2</h3>
                <div class="form-group">
                    <textarea id="game2Data" placeholder="Describe the second game in detail...

Include:
• Genre and core gameplay
• Key mechanics and features
• Art style and theme  
• What makes it unique
• Target platform

Example: 'Dark Souls - Challenging action RPG with stamina-based combat, interconnected world design, environmental storytelling...'"></textarea>
                </div>
            </div>
        </div>

        <div class="vs-divider">MASHUP</div>

        <button class="btn" onclick="createMashup()">🔥 Create Epic Mashup</button>

        <div id="response"></div>
    </div>

    <script>
        const apiUrl = window.location.origin;

        function showLoading() {
            document.getElementById('response').innerHTML = '<div class="loading">⚡ Fusing games together... This may take 30-60 seconds to craft the perfect mashup!</div>';
        }

        function showResponse(data, isError = false) {
            const responseDiv = document.getElementById('response');

            if (isError) {
                responseDiv.innerHTML = `<div class="response error">❌ Error: ${data.error || JSON.stringify(data, null, 2)}</div>`;
            } else if (data.success) {
                responseDiv.innerHTML = `
                    <div class="mashup-result">
                        <h2>🎮 Your Game Mashup Concept</h2>
                        <div class="mashup-meta">
                            <strong>Project Name:</strong> ${data.mashup_name}<br>
                            <strong>Concept ID:</strong> ${data.report_id}<br>
                            <strong>Created:</strong> ${data.generated_at}<br>
                            <strong>Source Fusion:</strong> Two unique games combined into one innovative concept
                        </div>
                        <div class="mashup-content">${formatMashupConcept(data.concept)}</div>
                    </div>
                `;

                // Scroll to results
                responseDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                responseDiv.innerHTML = `<div class="response error">❌ ${data.error || 'Unknown error occurred'}</div>`;
            }
        }

        function formatMashupConcept(concept) {
            // Enhanced formatting for the mashup concept
            return concept
                .replace(/## (.*)/g, '<h3 style="color: #667eea; margin-top: 30px; margin-bottom: 15px; border-left: 5px solid #667eea; padding-left: 15px;">$1</h3>')
                .replace(/### (.*)/g, '<h4 style="color: #764ba2; margin-top: 25px; margin-bottom: 12px;">$1</h4>')
                .replace(/\*\*(.*?)\*\*/g, '<strong style="color: #333;">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n\n/g, '</p><p style="margin-bottom: 15px;">')
                .replace(/^/, '<p style="margin-bottom: 15px;">')
                .replace(/$/, '</p>');
        }

        function showInfo(message) {
            document.getElementById('response').innerHTML = `<div class="response info">${message}</div>`;
        }

        async function createMashup() {
            console.log('🔄 createMashup called');

            const mashupName = document.getElementById('mashupName').value.trim();
            const game1Data = document.getElementById('game1Data').value.trim();
            const game2Data = document.getElementById('game2Data').value.trim();

            console.log('📝 Form data:', { mashupName, game1: game1Data.substring(0, 50) + '...', game2: game2Data.substring(0, 50) + '...' });

            // Validation
            if (!mashupName) {
                showInfo('🏷️ Please enter a name for your mashup project!');
                return;
            }

            if (!game1Data) {
                showInfo('🎮 Please describe the first game you want to mashup!');
                return;
            }

            if (!game2Data) {
                showInfo('🎮 Please describe the second game you want to mashup!');
                return;
            }

            if (game1Data.length < 50 || game2Data.length < 50) {
                showInfo('📝 Please provide more detailed descriptions for both games (at least a few sentences each)!');
                return;
            }

            const button = document.querySelector('.btn');
            if (button) {
                button.disabled = true;
                button.textContent = '⚡ Creating Mashup...';
            }

            showLoading();

            try {
                const response = await fetch(`${apiUrl}/api/create-mashup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mashup_name: mashupName,
                        game1_data: game1Data,
                        game2_data: game2Data
                    })
                });

                console.log('📡 Response status:', response.status);
                const data = await response.json();
                console.log('📄 Response data received');

                showResponse(data, !response.ok);
            } catch (error) {
                console.error('❌ Fetch error:', error);
                showResponse({ error: error.message }, true);
            } finally {
                // Re-enable button
                if (button) {
                    button.disabled = false;
                    button.textContent = '🔥 Create Epic Mashup';
                }
            }
        }

        // Add some helpful hints
        document.addEventListener('DOMContentLoaded', function() {
            const game1TextArea = document.getElementById('game1Data');
            const game2TextArea = document.getElementById('game2Data');

            game1TextArea.addEventListener('focus', function() {
                if (!this.value) {
                    showInfo('💡 Tip: The more detailed your game descriptions, the better the mashup will be! Include gameplay mechanics, art style, and what makes each game special.');
                }
            });
        });
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("🚀 Starting Game Mashup Creator API...")
    print("📧 Environment Variables Check:")
    print(f"   OPENAI_KEY: {'✅ Set' if os.environ.get('OPENAI_KEY') or os.environ.get('OPENAI_API_KEY') else '❌ Missing'}")

    # Get port from environment variable, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))

    # Check if we're in production (Railway sets PORT automatically)
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT')

    if is_production:
        print(f"🌐 Production mode detected, running on port {port}")
        print("💡 Note: In production, use 'gunicorn --bind 0.0.0.0:$PORT main:app' instead")
    else:
        print(f"🛠️ Development mode, running on port {port}")

    app.run(debug=False, host='0.0.0.0', port=port)