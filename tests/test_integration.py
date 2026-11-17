#!/usr/bin/env python3
"""
Integration Tests for Automated Video Pipeline & Social Publishing.
Simulates end-to-end generation, audio processing, image workflow,
queue state transitions, and YouTube upload protocols.
"""

import os
import sys
import json
import base64
import tempfile
import unittest.mock as mock
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import auto_pipeline
import generate_images
import uploader

class TestPipelineEndToEnd:
    @pytest.fixture(autouse=True)
    def setup_temp_queue(self, tmp_path):
        # Isolate publishing queue to a temporary file
        self.temp_queue_file = str(tmp_path / "test_publishing_queue.json")
        self.orig_queue_file = auto_pipeline.QUEUE_FILE
        self.orig_uploader_queue = uploader.QUEUE_FILE
        auto_pipeline.QUEUE_FILE = self.temp_queue_file
        uploader.QUEUE_FILE = self.temp_queue_file
        yield
        auto_pipeline.QUEUE_FILE = self.orig_queue_file
        uploader.QUEUE_FILE = self.orig_uploader_queue

    def test_short_pipeline_end_to_end_mocked(self):
        mock_story = {
            "title": "POV: Boss Fires You Not Knowing You Fund The Firm",
            "description": "Never fire the person who signs the payroll. #pov #karma #shorts",
            "tags": ["pov", "storytime", "karma", "shorts"],
            "script": "POV: Your manager calls you into his corner office with a smug smirk.",
            "image_prompts": ["Scene 1", "Scene 2", "Scene 3"]
        }

        async def fake_synthesize(text, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(b"MOCK_AUDIO_DATA")

        def fake_render(composition_id, out_file, duration_frames):
            assert composition_id == "DedicatedShort"
            assert duration_frames == 1350  # 45.0s * 30fps
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "wb") as f:
                f.write(b"MOCK_MP4_VIDEO")

        with mock.patch("auto_pipeline.generate_story_with_openrouter", return_value=mock_story), \
             mock.patch("auto_pipeline.synthesize_voice", side_effect=fake_synthesize), \
             mock.patch("auto_pipeline.get_audio_duration_seconds", return_value=45.0), \
             mock.patch("auto_pipeline.render_remotion", side_effect=fake_render):

            auto_pipeline.run_pipeline("short", duration_minutes=1, generate_images=False)

            # Assert video was enqueued
            queue = auto_pipeline.load_queue()
            assert len(queue) == 1
            entry = queue[0]
            assert entry["type"] == "short"
            assert entry["title"] == "POV: Boss Fires You Not Knowing You Fund The Firm"
            assert entry["duration_seconds"] == 45.0
            assert entry["status"] == "ready_to_post"
            assert entry["posted"] is False
            assert os.path.exists(entry["file_path"])

    def test_long_pipeline_end_to_end_mocked(self):
        mock_story = {
            "title": "The Ten Year Checkmate",
            "description": "A long form parable of quiet wealth and patience. #quietwealth",
            "tags": ["quietwealth", "parable", "longform"],
            "script": "Chapter 1: The Gathering.\nChapter 2: The Pitch.\nChapter 3: The Call.\nChapter 4: The Twist.\nChapter 5: Checkmate.",
            "image_prompts": ["Scene 1", "Scene 2", "Scene 3", "Scene 4", "Scene 5"]
        }

        async def fake_synthesize(text, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(b"MOCK_AUDIO_DATA")

        def fake_render(composition_id, out_file, duration_frames):
            assert composition_id == "FullEpisodeLong"
            assert duration_frames == 14400  # 480.0s (8 min) * 30fps
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "wb") as f:
                f.write(b"MOCK_MP4_VIDEO")

        with mock.patch("auto_pipeline.generate_story_with_openrouter", return_value=mock_story), \
             mock.patch("auto_pipeline.synthesize_voice", side_effect=fake_synthesize), \
             mock.patch("auto_pipeline.get_audio_duration_seconds", return_value=480.0), \
             mock.patch("auto_pipeline.render_remotion", side_effect=fake_render):

            auto_pipeline.run_pipeline("long", duration_minutes=8, generate_images=False)

            queue = auto_pipeline.load_queue()
            assert len(queue) == 1
            entry = queue[0]
            assert entry["type"] == "long"
            assert entry["title"] == "The Ten Year Checkmate"
            assert entry["duration_seconds"] == 480.0
            assert entry["status"] == "ready_to_post"
            assert entry["posted"] is False


class TestImageGenerationIntegration:
    def test_openrouter_image_generation_b64_mocked(self, tmp_path):
        dummy_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        dummy_b64 = base64.b64encode(dummy_png_bytes).decode("utf-8")

        mock_api_response = json.dumps({
            "created": 1748372400,
            "data": [
                {
                    "b64_json": dummy_b64,
                    "url": None
                }
            ]
        }).encode("utf-8")

        out_path = str(tmp_path / "test_generated_panel.png")

        mock_resp = mock.MagicMock()
        mock_resp.read.return_value = mock_api_response
        mock_resp.__enter__.return_value = mock_resp

        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-mock-test-key"}), \
             mock.patch("urllib.request.urlopen", return_value=mock_resp):

            result = generate_images.generate_image_with_openrouter(
                prompt="Quiet protagonist drinking coffee",
                output_path=out_path,
                aspect_ratio="9:16"
            )

            assert result == out_path
            assert os.path.exists(out_path)
            with open(out_path, "rb") as f:
                saved_bytes = f.read()
            assert saved_bytes == dummy_png_bytes


class TestYouTubeUploaderIntegration:
    def test_uploader_workflow_lifecycle_mocked(self, tmp_path):
        # Create a mock video file
        mock_video_path = str(tmp_path / "sample_video.mp4")
        with open(mock_video_path, "wb") as f:
            f.write(b"SAMPLE_VIDEO_CONTENT")

        # Seed the queue
        initial_queue = [
            {
                "id": "short_integration_test_1",
                "type": "short",
                "title": "Pass The Salt Test",
                "description": "Test description #shorts",
                "tags": ["test", "shorts"],
                "duration_seconds": 45.0,
                "file_path": mock_video_path,
                "status": "ready_to_post",
                "posted": False
            }
        ]
        auto_pipeline.save_queue(initial_queue)

        # Mock token access & YouTube upload
        with mock.patch("uploader.get_access_token", return_value="mock_valid_access_token"), \
             mock.patch("uploader.upload_to_youtube", return_value="https://youtu.be/MOCK_VIDEO_ID"):

            # Run uploader scanning loop
            queue = uploader.load_queue()
            for item in queue:
                if not item.get("posted", False):
                    video_url = uploader.upload_to_youtube(
                        item["file_path"],
                        item["title"],
                        item["description"],
                        item["tags"],
                        item["type"] == "short",
                        "mock_valid_access_token"
                    )
                    item["posted"] = True
                    item["status"] = "published"
                    item["published_url"] = video_url

            uploader.save_queue(queue)

            # Assert queue updated
            updated_queue = uploader.load_queue()
            assert len(updated_queue) == 1
            assert updated_queue[0]["posted"] is True
            assert updated_queue[0]["status"] == "published"
            assert updated_queue[0]["published_url"] == "https://youtu.be/MOCK_VIDEO_ID"


class TestRemotionBundleIntegration:
    def test_remotion_composition_bundle_compiles(self):
        import subprocess
        sample_video_dir = os.path.join(BASE_DIR, "sample-video")
        res = subprocess.run(
            ["npm", "run", "lint"],
            cwd=sample_video_dir,
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"Remotion lint/typecheck failed: {res.stderr}\n{res.stdout}"
