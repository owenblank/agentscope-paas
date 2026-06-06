"""
Runtime Validator Module

Provides utilities for validating AgentScope Runtime installation and
providing clear error messages and installation guidance.
"""

import sys
import subprocess
import logging
from typing import Dict, Any, Optional, Tuple
import platform
from ..utils.logger import get_logger


class RuntimeValidator:
    """
    Runtime Validator for checking AgentScope Runtime availability
    and providing installation guidance.
    """

    def __init__(self):
        """Initialize Runtime Validator"""
        self.logger = get_logger(__name__)
        self.runtime_available = False
        self.runtime_version = None
        self.installation_guide = self._create_installation_guide()
        self._check_runtime_status()

    def _check_runtime_status(self) -> None:
        """Check if AgentScope Runtime is available"""
        try:
            import agentscope.runtime
            self.runtime_available = True

            # Try to get version
            try:
                import importlib.metadata
                self.runtime_version = importlib.metadata.version("agentscope-runtime")
            except Exception:
                self.runtime_version = "unknown"

            self.logger.info(f"AgentScope Runtime is available (version: {self.runtime_version})")

        except ImportError as e:
            self.runtime_available = False
            self.logger.warning(f"AgentScope Runtime not available: {str(e)}")

    def _create_installation_guide(self) -> Dict[str, str]:
        """
        Create installation guide for different environments

        Returns:
            Installation guide dictionary
        """
        return {
            "pip": "pip install agentscope-runtime",
            "pip_with_version": "pip install 'agentscope-runtime>=1.0.0'",
            "conda": "conda install -c conda-forge agentscope-runtime",
            "requirements": "agentscope-runtime>=1.0.0",
            "from_source": "git clone https://github.com/modelscope/agentscope.git && cd agentscope && pip install -e .[runtime]",
            "verify_command": "python -c 'import agentscope.runtime; print(\"Runtime installed successfully\")'"
        }

    def is_runtime_available(self) -> bool:
        """
        Check if Runtime is available

        Returns:
            True if Runtime available, False otherwise
        """
        return self.runtime_available

    def get_runtime_status(self) -> Dict[str, Any]:
        """
        Get detailed Runtime status information

        Returns:
            Runtime status dictionary
        """
        status = {
            "available": self.runtime_available,
            "version": self.runtime_version,
            "python_version": sys.version,
            "platform": platform.system(),
            "platform_details": platform.platform(),
            "installation_commands": self.installation_guide if not self.runtime_available else None,
            "features": self._get_available_features() if self.runtime_available else []
        }

        return status

    def _get_available_features(self) -> list:
        """
        Get list of available Runtime features

        Returns:
            List of available feature names
        """
        features = []

        if not self.runtime_available:
            return features

        try:
            from agentscope.runtime import (
                AgentApp,
                LocalDeployManager,
                Runner,
                ServiceStatusCode
            )
            features.extend([
                "AgentApp",
                "LocalDeployManager",
                "Runner",
                "ServiceStatus",
                "Streaming",
                "HealthChecks"
            ])

            # Check for additional features
            try:
                from agentscope.runtime.sandbox import BaseSandbox
                features.append("SandboxSupport")
            except ImportError:
                pass

            try:
                from agentscope.runtime.monitoring import MetricsCollector
                features.append("AdvancedMonitoring")
            except ImportError:
                pass

        except Exception as e:
            self.logger.error(f"Feature detection failed: {str(e)}")

        return features

    def get_installation_help(self) -> str:
        """
        Get detailed installation help text

        Returns:
            Installation help string
        """
        help_text = """
# AgentScope Runtime Installation Guide

## Why Runtime is Needed

AgentScope Runtime provides production-level deployment capabilities:
- **AgentApp Deployment**: Deploy agents as HTTP services
- **Lifecycle Management**: Automatic startup, shutdown, and cleanup
- **Health Monitoring**: Built-in health checks and status monitoring
- **Streaming Support**: Real-time streaming responses
- **Sandbox Execution**: Secure code execution environments
- **Production Features**: Load balancing, auto-restart, resource management

## Installation Methods

### Method 1: Using pip (Recommended)
```bash
pip install agentscope-runtime
```

### Method 2: Using pip with version specification
```bash
pip install 'agentscope-runtime>=1.0.0'
```

### Method 3: Using conda
```bash
conda install -c conda-forge agentscope-runtime
```

### Method 4: From source
```bash
git clone https://github.com/modelscope/agentscope.git
cd agentscope
pip install -e .[runtime]
```

## Verification

After installation, verify it's working:
```bash
python -c "import agentscope.runtime; print('Runtime installed successfully')"
```

## Troubleshooting

### Issue: Import Errors
If you see import errors after installation:
```bash
# Reinstall with dependencies
pip install --force-reinstall agentscope-runtime

# Or upgrade pip first
pip install --upgrade pip
pip install agentscope-runtime
```

### Issue: Version Conflicts
If you have version conflicts with AgentScope:
```bash
# Upgrade both packages together
pip install --upgrade agentscope agentscope-runtime
```

### Issue: Permission Errors
If you get permission errors:
```bash
# Use user directory installation
pip install --user agentscope-runtime

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install agentscope-runtime
```

## Dependencies

AgentScope Runtime requires:
- Python >= 3.8
- agentscope >= 1.0.19
- FastAPI >= 0.100.0
- uvicorn >= 0.23.0

These will be installed automatically with agentscope-runtime.

## Next Steps

After installation, you can:
1. Create Runtime-enabled agents
2. Deploy agents as HTTP services
3. Use health monitoring and lifecycle management
4. Enable streaming responses
5. Configure sandbox execution (optional)

For more information, see the AgentScope Runtime documentation.
"""
        return help_text

    def check_runtime_compatibility(self) -> Tuple[bool, list[str]]:
        """
        Check if current environment is compatible with Runtime

        Returns:
            (is_compatible, list of issues) tuple
        """
        issues = []

        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python version {sys.version_info} is too old. Runtime requires Python >= 3.8")

        # Check for required packages if Runtime is installed
        if self.runtime_available:
            try:
                import fastapi
                import uvicorn
            except ImportError as e:
                issues.append(f"Missing required dependency: {str(e)}")

        # Check platform compatibility
        system = platform.system()
        if system not in ["Linux", "Darwin", "Windows"]:
            issues.append(f"Platform {system} may not be fully supported")

        return (len(issues) == 0, issues)

    def get_runtime_quickstart(self) -> str:
        """
        Get quick start guide for Runtime usage

        Returns:
            Quick start guide string
        """
        quickstart = """
# AgentScope Runtime Quick Start

## 1. Install Runtime (if not already installed)
```bash
pip install agentscope-runtime
```

## 2. Verify Installation
```bash
python -c "import agentscope.runtime; print('Runtime ready!')"
```

## 3. Create a Runtime-Enabled Agent
Use the PaaS configuration system with Runtime extension:

```yaml
agent_metadata:
  agent_name: "RuntimeAgent"
  agent_id: "runtime_agent"
  agent_type: "DialogAgent"
  description: "Agent with Runtime support"

runtime_config:
  deployment_mode: "runtime"
  service:
    host: "localhost"
    port: 8080
  lifecycle:
    auto_start: true
    idle_timeout_minutes: 30
```

## 4. Deploy the Agent
```python
from agentscope_paas.core.runtime_manager import get_runtime_manager
from agentscope_paas.config.loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader("my_agent.yaml")
config_loader.load()

# Get Runtime manager and deploy
runtime_manager = get_runtime_manager(config_loader)
success = runtime_manager.create_and_deploy_agent(
    host="localhost",
    port=8080
)

if success:
    print("Agent deployed successfully!")
    print(f"Service URL: {runtime_manager.deployment_url}")
```

## 5. Use the Deployed Agent
```python
# Get runner for conversation
runner = runtime_manager.get_runner()

# Chat with the agent
response = await runner.query("Hello, how are you?")
print(response)
```

## 6. Monitor Health
```python
# Check agent health
health_info = runtime_manager.check_health()
print(f"Health status: {health_info['status']}")
print(f"Deployment status: {health_info['deployment_status']}")
```

## 7. Stop and Cleanup
```python
# Stop the agent when done
runtime_manager.stop_agent(cleanup=True)
```

## Key Features

- **Automatic Deployment**: One-command deployment as HTTP service
- **Health Monitoring**: Built-in health checks and status monitoring
- **Lifecycle Management**: Auto-start, idle timeout, graceful shutdown
- **Streaming Support**: Real-time streaming responses
- **Production Ready**: Resource limits, error handling, logging

## Next Steps

- Explore Runtime configuration options
- Set up health monitoring and alerts
- Configure sandbox execution for security
- Implement streaming responses
- Add Runtime monitoring and metrics

For detailed documentation, see the AgentScope Runtime guides.
"""
        return quickstart

    def print_runtime_status(self) -> None:
        """Print detailed Runtime status to console"""
        status = self.get_runtime_status()

        print("\n" + "="*60)
        print("AgentScope Runtime Status")
        print("="*60)

        if status["available"]:
            print(f"✓ Runtime Available: Yes (version: {status['version']})")
            print(f"✓ Python Version: {status['python_version']}")
            print(f"✓ Platform: {status['platform_details']}")

            if status["features"]:
                print("✓ Available Features:")
                for feature in status["features"]:
                    print(f"  - {feature}")
        else:
            print("✗ Runtime Available: No")
            print(f"✗ Python Version: {status['python_version']}")
            print(f"✗ Platform: {status['platform_details']}")

            print("\nInstallation Commands:")
            for method, command in self.installation_guide.items():
                print(f"  {method}: {command}")

            print("\n" + self.get_installation_help())

        print("="*60 + "\n")


def create_runtime_validator() -> RuntimeValidator:
    """
    Create Runtime Validator instance

    Returns:
        RuntimeValidator instance
    """
    return RuntimeValidator()


def check_runtime_availability() -> bool:
    """
    Quick check if Runtime is available

    Returns:
        True if Runtime available, False otherwise
    """
    try:
        import agentscope.runtime
        return True
    except ImportError:
        return False


def get_runtime_installation_command(package_manager: str = "pip") -> str:
    """
    Get installation command for specific package manager

    Args:
        package_manager: Package manager name (pip, conda, etc.)

    Returns:
        Installation command string
    """
    commands = {
        "pip": "pip install agentscope-runtime",
        "pip-versions": "pip install 'agentscope-runtime>=1.0.0'",
        "conda": "conda install -c conda-forge agentscope-runtime",
        "poetry": "poetry add agentscope-runtime",
        "pipenv": "pipenv install agentscope-runtime"
    }

    return commands.get(package_manager, commands["pip"])


def validate_runtime_environment() -> Tuple[bool, list[str], list[str]]:
    """
    Validate entire Runtime environment

    Returns:
        (is_valid, warnings, errors) tuple
    """
    warnings = []
    errors = []

    validator = RuntimeValidator()

    # Check Runtime availability
    if not validator.is_runtime_available():
        errors.append("AgentScope Runtime is not installed")

    # Check compatibility
    is_compatible, compatibility_issues = validator.check_runtime_compatibility()
    if not is_compatible:
        errors.extend(compatibility_issues)

    # Check for warnings
    if validator.runtime_version:
        # Check if version is outdated
        try:
            from packaging import version
            current_version = version.parse(validator.runtime_version)
            minimum_version = version.parse("1.0.0")

            if current_version < minimum_version:
                warnings.append(
                    f"Runtime version {validator.runtime_version} is outdated. "
                    f"Consider upgrading to >=1.0.0"
                )
        except ImportError:
            pass  # Skip version check if packaging not available

    return (len(errors) == 0, warnings, errors)