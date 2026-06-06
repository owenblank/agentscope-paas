# tests/test_cli.py
import pytest
from agentscope_paas.cli.main import main
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

@patch('sys.argv', ['agentscope-paas', '--help'])
def test_cli_help():
    """Test CLI help display"""
    with pytest.raises(SystemExit):
        main()

@patch('sys.argv', ['agentscope-paas', 'run', 'test.yaml'])
def test_cli_run_command():
    """Test CLI run command parsing"""
    with patch('agentscope_paas.cli.main.Launcher') as mock_launcher:
        mock_launcher.return_value.launch_agent.return_value = True
        with patch('pathlib.Path.exists', return_value=True):
            with patch('agentscope_paas.config.loader.ConfigLoader') as mock_loader:
                mock_loader.return_value.load.return_value = (True, {}, [])
                main()
                mock_launcher.assert_called_once()

@patch('sys.argv', ['agentscope-paas', 'batch', '/path/to/configs'])
def test_cli_batch_command():
    """Test CLI batch command parsing"""
    with patch('agentscope_paas.cli.main.ConfigProcessor') as mock_processor:
        main()
        mock_processor.assert_called_once()