# YouTube Video Downloader and Info API

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description
The YouTube Video Downloader and Info API is a Flask-based Python project that allows you to download YouTube videos and retrieve video information using Pytube. This versatile tool provides two main functionalities:

1. **Download Video:** You can specify the video URL and resolution to download YouTube videos directly to your local machine.

2. **Get Video Info:** You can retrieve detailed information about a YouTube video, including its title, author, length, views, description, and publish date.

This project is designed to simplify the process of interacting with YouTube content programmatically.

## Features
- Download YouTube videos in various resolutions.
- Retrieve comprehensive information about YouTube videos.
- Error handling for reliable performance.
- JSON API endpoints for easy integration into other applications.

## Libraries and Technologies Used
- Python 3.x
- Flask for building the API.
- Pytube for interacting with YouTube content.
- re for URL validation.

## Usage
1. Clone this repository: `git clone https://github.com/zararashraf/youtube-video-downloader-api.git`
2. Install the required libraries: `pip install flask pytube flask-cors`
3. Run the Flask application: `python main.py`
4. Access the API endpoints using HTTP requests (e.g., POST requests in Postman).

## API Endpoints

### Download Video by Resolution
- **Endpoint:** `/download/<resolution>`
- **HTTP Method:** POST
- **Request Body:** JSON
    ```json
    {
        "url": "https://www.youtube.com/watch?v=VIDEO_ID"
    }
    ```

### Get Video Info
- **Endpoint:** `/video_info`
- **HTTP Method:** POST
- **Request Body:** JSON
    ```json
    {
        "url": "https://www.youtube.com/watch?v=VIDEO_ID"
    }
    ```

## Screenshots
### Downloading a Video
![image](https://github.com/zararashraf/youtube-video-downloader-api/assets/36181292/edad60c8-27fc-4ed0-8243-21ffc4cc16cc)

### Retrieving Info
![image](https://github.com/zararashraf/youtube-video-downloader-api/assets/36181292/e0e3aeb3-fa97-41c7-9d89-971f2cda421e)


## Code Repository
You can access the source code for this project on [GitHub](https://github.com/zararashraf/youtube-video-downloader-api/blob/main/main.py).

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). You are free to use, modify, and distribute the code while providing appropriate attribution.
