from flask import Flask, request, send_file, render_template_string
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import re

app = Flask(__name__)

# HTML template for the main page
TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>PotHole</title>
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.9.0/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        body {
            padding: 50px;
            background-color: #f0f0f0;
        }
        .search-form {
            max-width: 600px;
            margin: 0 auto;
        }
        .search-button {
            min-width: 100px;
        }
        .animated-heading {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            display: inline-block;
            position: relative;
        }
        .animated-heading .pot, .animated-heading .hole {
            animation: dance 5s infinite;
            display: inline-block;
        }
        .animated-heading .pot {
            animation: move-up-down 5s infinite linear;
            color: #ff6347; /* Red color for 'Pot' */
        }
        .animated-heading .hole {
            animation: move-left-right 5s infinite linear;
            color: #4fc3f7; /* Blue color for 'Hole' */
        }
        @keyframes move-up-down {
            0% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-10px);
            }
            100% {
                transform: translateY(0);
            }
        }
        @keyframes move-left-right {
            0% {
                transform: translateX(0);
            }
            50% {
                transform: translateX(10px);
            }
            100% {
                transform: translateX(0);
            }
        }
        @keyframes dance {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .animated-heading .text {
            animation: color-change 10s infinite alternate;
            animation-timing-function: ease-in-out;
        }
        @keyframes color-change {
            0% { color: #ff6347; } /* Red */
            25% { color: #ffbb33; } /* Orange */
            50% { color: #66bb6a; } /* Green */
            75% { color: #4fc3f7; } /* Blue */
            100% { color: #ab47bc; } /* Purple */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mt-5">
            <h1 class="animated-heading">
                <span class="pot">Pot</span><span class="hole">Hole</span>
            </h1>
            <form action="/download" method="post" class="search-form">
                <div class="input-group mb-3">
                    <input type="text" id="url" name="url" class="form-control" placeholder="Enter Video URL" required>
                    <div class="input-group-append">
                        <button class="btn btn-primary search-button" type="submit">Download</button>
                    </div>
                </div>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="bi bi-youtube"></i></span>
                    </div>
                    <input type="text" id="youtube-url" name="youtube-url" class="form-control" placeholder="YouTube Video URL">
                </div>
                <div class="input-group mt-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="bi bi-twitter"></i></span>
                    </div>
                    <input type="text" id="twitter-url" name="twitter-url" class="form-control" placeholder="Twitter Video URL">
                </div>
                <div class="input-group mt-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="bi bi-facebook"></i></span>
                    </div>
                    <input type="text" id="facebook-url" name="facebook-url" class="form-control" placeholder="Facebook Video URL">
                </div>
            </form>
        </div>
    </div>
    <!-- Bootstrap JS and dependencies -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    if 'youtube.com' in url or 'youtu.be' in url:
        return download_youtube_video(url)
    elif 'twitter.com' in url or 't.co' in url:
        return download_twitter_video(url)
    elif 'facebook.com' in url:
        return download_facebook_video(url)
    else:
        return "Unsupported URL"

def download_youtube_video(url):
    # Your existing implementation for YouTube video download
    pass

def download_twitter_video(url):
    try:
        # Ensure the URL is in the correct format
        if not url.startswith('https://twitter.com/') and not url.startswith('https://t.co/'):
            raise ValueError("Invalid Twitter URL")

        # Extract video ID from URL
        video_id_match = re.search(r'https://twitter.com/.+/status/(\d+)', url)
        if not video_id_match:
            raise ValueError("Invalid Twitter video URL")

        video_id = video_id_match.group(1)

        # Construct the video URL
        video_url = f'https://twitter.com/i/videos/{video_id}'

        # Send a request to get the video page
        response = requests.get(video_url)
        response.raise_for_status()

        # Parse the JSON response to get the video URL
        data = response.json()
        formats = data['media']['track']['playbackUrl']

        # Choose the highest quality video format
        video_format = formats[0]['url']

        # Download the video
        video_response = requests.get(video_format)
        video_bytes = BytesIO(video_response.content)
        return send_file(video_bytes, as_attachment=True, download_name='twitter_video.mp4')

    except requests.exceptions.RequestException as e:
        return f"Failed to download video: {str(e)}"
    except Exception as e:
        return f"Failed to download video: {str(e)}"

def download_facebook_video(url):
    try:
        # Send a request to get the HTML content of the Facebook page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad requests

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the video URL in the embedded video tag
        video_elem = soup.find('video')
        if video_elem and video_elem.has_attr('src'):
            video_url = video_elem['src']
            video_response = requests.get(video_url)
            video_bytes = BytesIO(video_response.content)
            return send_file(video_bytes, as_attachment=True, download_name='facebook_video.mp4')
        else:
            return "Failed to find Facebook video URL"

    except requests.exceptions.RequestException as e:
        return f"Failed to download video: {str(e)}"
    except Exception as e:
        return f"Failed to download video: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
