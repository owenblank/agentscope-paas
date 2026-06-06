# tests/test_interactive.py
import pytest
from unittest.mock import Mock, patch
from agentscope_paas.cli.interactive import InteractiveSession

def test_interactive_session_creation():
    """Test interactive session initialization"""
    agents = {
        "agent1": Mock(),
        "agent2": Mock()
    }

    session = InteractiveSession(agents)
    assert session.agents == agents
    assert session.running == False

def test_interactive_session_display_welcome():
    """Test welcome message display"""
    agents = {"agent1": Mock()}
    session = InteractiveSession(agents)

    with patch('builtins.print') as mock_print:
        session.display_welcome()
        mock_print.assert_called()

@patch('builtins.input', return_value='你好')
def test_interactive_session_get_user_input(mock_input):
    """Test getting user input"""
    agents = {"agent1": Mock()}
    session = InteractiveSession(agents)

    user_input = session.get_user_input()
    assert user_input == "你好"
