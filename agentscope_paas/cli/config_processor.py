# agentscope_paas/cli/config_processor.py
import glob
from pathlib import Path
from typing import List, Dict, Any

from agentscope_paas.utils.logger import get_logger


class ConfigProcessor:
    """Processes configuration files for CLI operations"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def scan_directory(self, directory: str, pattern: str = "*.yaml") -> List[str]:
        """Scan directory for configuration files"""
        dir_path = Path(directory)

        if not dir_path.exists():
            self.logger.error(f"Directory does not exist: {directory}")
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Use glob to find matching files
        search_pattern = str(dir_path / pattern)
        config_files = glob.glob(search_pattern)

        self.logger.info(f"Found {len(config_files)} config files in {directory}")
        return sorted(config_files)

    def classify_config(self, config: Dict[str, Any]) -> str:
        """Classify configuration type"""
        if "team_metadata" in config or "team_name" in config:
            return "team"
        elif "agent_metadata" in config or "agent_name" in config:
            return "single"
        else:
            return "unknown"
