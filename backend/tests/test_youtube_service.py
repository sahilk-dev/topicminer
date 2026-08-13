import pytest
from app.services.youtube import extract_video_id

def test_extract_video_id_standard_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_short_url():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_with_extra_params():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_invalid_url_raises():
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/not-a-youtube-link")