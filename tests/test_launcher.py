# tests/test_launcher.py
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import the module directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentscope_paas.cli.launcher import Launcher

def test_launcher_initialization():
    """Test launcher initialization"""
    launcher = Launcher(mode="interactive")
    assert launcher.mode == "interactive"
    assert launcher.agents == {}

def test_launch_agent_success():
    """Test successful agent launch"""
    launcher = Launcher()
    config = {
        "agent_metadata": {"name": "test_agent"},
        "model_config": {"model_name": "gpt-3.5"},
        "prompt_config": {"system_prompt": "You are a helper"}
    }

    with patch('agentscope_paas.factory.agent_factory.AgentFactory') as mock_factory_cls, \
         patch('agentscope_paas.config.loader.ConfigLoader') as mock_loader_cls:

        mock_loader = Mock()
        mock_loader_cls.return_value = mock_loader

        mock_factory = Mock()
        mock_factory_cls.return_value = mock_factory

        mock_agent = Mock()
        mock_factory.create_agent.return_value = mock_agent

        result = launcher.launch_agent(config, "agent1")
        assert result == True
        assert "agent1" in launcher.agents

def test_launch_agent_failure():
    """Test agent launch failure handling"""
    launcher = Launcher()
    config = {"invalid": "config"}

    with patch('agentscope_paas.factory.agent_factory.AgentFactory') as mock_factory_cls, \
         patch('agentscope_paas.config.loader.ConfigLoader') as mock_loader_cls:

        mock_loader = Mock()
        mock_loader_cls.return_value = mock_loader

        mock_factory = Mock()
        mock_factory_cls.return_value = mock_factory
        mock_factory.create_agent.side_effect = Exception("Creation failed")

        result = launcher.launch_agent(config, "agent1")
        assert result == False
