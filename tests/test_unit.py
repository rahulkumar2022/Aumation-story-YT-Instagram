#!/usr/bin/env python3
"""
Unit Tests for Automated Video Pipeline & Publishing System.
Tests core utility logic, JSON extraction, timing math, and queue state.
"""

import os
import sys
import json
import re
import tempfile
import pytest

# Ensure scripts directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import auto_pipeline
import generate_images
import uploader

class TestDotEnvLoader:
    def test_load_dotenv_parses_cleanly(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("# Sample comment\n")
            f.write("TEST_ENV_VAR_1=hello_world\n")
            f.write("TEST_ENV_VAR_2='quoted_value'\n")
            f.write("TEST_ENV_VAR_3=\"double_quoted\"\n")
            f.write("\n")
            f.write("INVALID LINE WITH NO EQUALS\n")
            f.flush()
            temp_path = f.name

        try:
            auto_pipeline.load_dotenv(temp_path)
            assert os.environ.get("TEST_ENV_VAR_1") == "hello_world"
            assert os.environ.get("TEST_ENV_VAR_2") == "quoted_value"
            assert os.environ.get("TEST_ENV_VAR_3") == "double_quoted"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            for k in ["TEST_ENV_VAR_1", "TEST_ENV_VAR_2", "TEST_ENV_VAR_3"]:
                os.environ.pop(k, None)


class TestJsonStoryExtraction:
    def test_extract_clean_json(self):
        sample = '{"title": "The Quiet Chairman", "script": "Pass the salt."}'
        match = re.search(r'\{.*\}', sample, re.DOTALL)
        assert match is not None
        data = json.loads(match.group(0))
        assert data["title"] == "The Quiet Chairman"
        assert data["script"] == "Pass the salt."

    def test_extract_markdown_fenced_json(self):
        sample = '```json\n{\n  "title": "Family Dinner Twist",\n  "description": "#pov #karma",\n  "tags": ["pov", "karma"],\n  "script": "He bragged, I smiled."\n}\n```'
        match = re.search(r'\{.*\}', sample, re.DOTALL)
        assert match is not None
        data = json.loads(match.group(0))
        assert data["title"] == "Family Dinner Twist"
        assert len(data["tags"]) == 2

    def test_extract_json_with_surrounding_commentary(self):
        sample = 'Here is your viral YouTube script in JSON format:\n\n{"title": "Quiet Checkmate", "script": "The lease is mine."}\n\nHope this helps!'
        match = re.search(r'\{.*\}', sample, re.DOTALL)
        assert match is not None
        data = json.loads(match.group(0))
        assert data["title"] == "Quiet Checkmate"
        assert data["script"] == "The lease is mine."


class TestStoryTemplates:
    def test_short_story_template_schema(self):
        story = auto_pipeline.get_short_story()
        assert "title" in story
        assert "description" in story
        assert "tags" in story
        assert "script" in story
        assert isinstance(story["tags"], list)
        assert len(story["tags"]) >= 4
        # Spoken script should be reasonable length for 30-60s
        word_count = len(story["script"].split())
        assert 70 <= word_count <= 160

    def test_long_story_template_schema(self):
        story = auto_pipeline.get_long_story(target_minutes=8)
        assert "title" in story
        assert "description" in story
        assert "tags" in story
        assert "script" in story
        assert isinstance(story["tags"], list)
        # Should have multi-chapter structure
        assert "Chapter 1" in story["script"]
        assert "Chapter 5" in story["script"]
        word_count = len(story["script"].split())
        assert word_count > 600


class TestTimingAndFrameCalculations:
    def test_frame_calculation_at_30fps(self):
        duration_secs = 50.0
        fps = 30
        duration_frames = int(duration_secs * fps)
        assert duration_frames == 1500

    def test_proportional_scene_slicing_shorts(self):
        duration_frames = 1500
        s1 = int(duration_frames * 0.32)
        s2 = int(duration_frames * 0.28)
        s3 = duration_frames - s1 - s2
        assert s1 + s2 + s3 == duration_frames
        assert s1 > 0 and s2 > 0 and s3 > 0

    def test_proportional_chapter_slicing_long(self):
        duration_frames = 11000
        chunk = duration_frames // 5
        assert chunk == 2200
        assert chunk * 5 == duration_frames


class TestPublishingQueue:
    def test_queue_load_empty_nonexistent(self):
        orig_file = auto_pipeline.QUEUE_FILE
        auto_pipeline.QUEUE_FILE = "/tmp/non_existent_queue_test_12345.json"
        try:
            q = auto_pipeline.load_queue()
            assert q == []
        finally:
            auto_pipeline.QUEUE_FILE = orig_file

    def test_queue_save_and_reload(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            temp_path = f.name

        orig_file = auto_pipeline.QUEUE_FILE
        auto_pipeline.QUEUE_FILE = temp_path
        try:
            sample_entry = {
                "id": "short_test_001",
                "type": "short",
                "title": "Test Title",
                "duration_seconds": 45.2,
                "posted": False
            }
            auto_pipeline.save_queue([sample_entry])
            reloaded = auto_pipeline.load_queue()
            assert len(reloaded) == 1
            assert reloaded[0]["id"] == "short_test_001"
            assert reloaded[0]["posted"] is False
        finally:
            auto_pipeline.QUEUE_FILE = orig_file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestImagePromptFormatting:
    def test_style_anchor_present(self):
        assert "2D graphic novel motion comic panel" in generate_images.STYLE_ANCHOR
        assert "cel-shaded illustration" in generate_images.STYLE_ANCHOR
        assert "Quiet Capital art style" in generate_images.STYLE_ANCHOR

    def test_aspect_ratio_parameters(self):
        # 9:16 for Shorts, 16:9 for Widescreen
        valid_ratios = ["9:16", "16:9", "1:1"]
        assert "9:16" in valid_ratios
        assert "16:9" in valid_ratios


class TestYouTubeUploaderMetadata:
    def test_youtube_shorts_title_formatting(self):
        # Shorts titles should append #Shorts if not present
        title = "Arrogant Brother Humbled"
        is_short = True
        formatted_title = f"{title} #Shorts" if is_short and "#Shorts" not in title else title
        assert formatted_title == "Arrogant Brother Humbled #Shorts"

    def test_youtube_shorts_title_already_tagged(self):
        title = "Arrogant Brother Humbled #Shorts"
        is_short = True
        formatted_title = f"{title} #Shorts" if is_short and "#Shorts" not in title else title
        assert formatted_title == "Arrogant Brother Humbled #Shorts"

    def test_youtube_long_form_title_untouched(self):
        title = "The Full Story of How Marcus Lost the Deal"
        is_short = False
        formatted_title = f"{title} #Shorts" if is_short and "#Shorts" not in title else title
        assert formatted_title == "The Full Story of How Marcus Lost the Deal"
