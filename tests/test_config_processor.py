# tests/test_config_processor.py
import pytest
import tempfile
import os
from pathlib import Path
from agentscope_paas.cli.config_processor import ConfigProcessor

def test_scan_directory_with_yaml_files(tmp_path):
    """Test scanning directory for YAML files"""
    # Create test files
    (tmp_path / "config1.yaml").write_text("agent_metadata: {name: test1}")
    (tmp_path / "config2.yaml").write_text("agent_metadata: {name: test2}")
    (tmp_path / "README.md").write_text("documentation")
    (tmp_path / "config.txt").write_text("not yaml")

    processor = ConfigProcessor()
    configs = processor.scan_directory(str(tmp_path), pattern="*.yaml")

    assert len(configs) == 2
    assert any("config1.yaml" in c for c in configs)
    assert any("config2.yaml" in c for c in configs)

def test_scan_directory_empty(tmp_path):
    """Test scanning empty directory"""
    processor = ConfigProcessor()
    configs = processor.scan_directory(str(tmp_path), pattern="*.yaml")

    assert len(configs) == 0

def test_classify_single_agent_config():
    """Test classifying single agent configuration"""
    processor = ConfigProcessor()
    config = {
        "agent_metadata": {"name": "test_agent"},
        "model_config": {"model_name": "gpt-3.5"},
        "prompt_config": {"system_prompt": "You are a helper"}
    }

    config_type = processor.classify_config(config)
    assert config_type == "single"

def test_classify_team_config():
    """Test classifying team configuration"""
    processor = ConfigProcessor()
    config = {
        "team_metadata": {"name": "dev_team"},
        "agents": ["agent1", "agent2"]
    }

    config_type = processor.classify_config(config)
    assert config_type == "team"
