# tests/test_error_handler.py
import pytest
import sys
import os

# Import the error_handler module directly without going through the package __init__
import importlib.util

# Load the error_handler module directly
spec = importlib.util.spec_from_file_location(
    "error_handler",
    os.path.join(os.path.dirname(__file__), "..", "agentscope_paas", "cli", "error_handler.py")
)
error_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(error_handler)

ErrorHandler = error_handler.ErrorHandler

def test_handle_config_error_strict_mode():
    """Test config error handling in strict mode"""
    handler = ErrorHandler(strict=True)
    error = Exception("Syntax error in YAML")

    with pytest.raises(SystemExit):
        handler.handle_config_error("test.yaml", error, strict=True)

def test_handle_config_error_non_strict_mode():
    """Test config error handling in non-strict mode"""
    handler = ErrorHandler(strict=False)
    error = Exception("Syntax error in YAML")

    # Should not raise exception
    handler.handle_config_error("test.yaml", error, strict=False)

def test_handle_launch_error_continue():
    """Test launch error handling with continue flag"""
    handler = ErrorHandler()
    error = Exception("Agent creation failed")

    # Should not raise exception
    handler.handle_launch_error("agent1", error, continue_on_error=True)

def test_handle_launch_error_stop():
    """Test launch error handling without continue flag"""
    handler = ErrorHandler()
    error = Exception("Agent creation failed")

    with pytest.raises(SystemExit):
        handler.handle_launch_error("agent1", error, continue_on_error=False)
