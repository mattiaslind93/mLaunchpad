"""Core logic for HomeLaunchPad - reads projects, sequences, shots and builds environment."""

import json
import os
from pathlib import Path
from typing import Optional


class HomeLaunchPad:
    """Main class for managing project/sequence/shot selection and environment."""

    CONFIG_PATH = Path.home() / ".homelaunchpad" / "config.json"

    # Folders to exclude from project/sequence/shot listings
    EXCLUDED_FOLDERS = {
        "_projData",
        "_shotData",
        "dailies",
        "delivery",
        "editorial",
        "incoming",
        "personal",
        "tools",
    }

    def __init__(self):
        self.config = self._load_config()
        self.current_source: str = self.config.get("current_source", "milford")
        self.current_project: Optional[str] = self.config.get("last_project")
        self.current_sequence: Optional[str] = self.config.get("last_sequence")
        self.current_shot: Optional[str] = self.config.get("last_shot")

    def _load_config(self) -> dict:
        """Load configuration from JSON file, creating default if not exists."""
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH, "r") as f:
                config = json.load(f)
                # Migrate old config to new format with sources
                if "sources" not in config:
                    config = self._migrate_config(config)
                return config

        # Create default config with sources
        default_config = {
            "sources": {
                "milford": {
                    "name": "Milford",
                    "jobs_path": "/var/mnt/jack/JOBS",
                    "system_path": "/var/mnt/jack/SYSTEM",
                },
                "private": {
                    "name": "Privat",
                    "jobs_path": "/home/mlind/Insync/mattiaslind93@gmail.com/Google Drive/Pipeline",
                    "system_path": "/var/mnt/jack/SYSTEM",
                },
            },
            "current_source": "private",
            "user_name": os.environ.get("USER", "unknown"),
            "blender_executable": "/home/mlind/Dokument/Blender/blender_config/blender-5.0.1-linux-x64/blender",
            "last_project": None,
            "last_sequence": None,
            "last_shot": None,
        }
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    def _migrate_config(self, old_config: dict) -> dict:
        """Migrate old config format to new format with sources."""
        new_config = {
            "sources": {
                "milford": {
                    "name": "Milford",
                    "jobs_path": old_config.get("jobs_path", "/var/mnt/jack/JOBS"),
                    "system_path": old_config.get("system_path", "/var/mnt/jack/SYSTEM"),
                },
                "private": {
                    "name": "Privat",
                    "jobs_path": "/home/mlind/Insync/mattiaslind93@gmail.com/Google Drive/Pipeline",
                    "system_path": old_config.get("system_path", "/var/mnt/jack/SYSTEM"),
                },
            },
            "current_source": "private",
            "user_name": old_config.get("user_name", os.environ.get("USER", "unknown")),
            "blender_executable": old_config.get("blender_executable", ""),
            "last_project": old_config.get("last_project"),
            "last_sequence": old_config.get("last_sequence"),
            "last_shot": old_config.get("last_shot"),
        }
        # Save migrated config
        with open(self.CONFIG_PATH, "w") as f:
            json.dump(new_config, f, indent=2)
        return new_config

    def save_config(self):
        """Save current configuration to JSON file."""
        self.config["current_source"] = self.current_source
        self.config["last_project"] = self.current_project
        self.config["last_sequence"] = self.current_sequence
        self.config["last_shot"] = self.current_shot
        with open(self.CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_sources(self) -> dict[str, dict]:
        """Return all available sources."""
        return self.config.get("sources", {})

    def get_source_names(self) -> list[tuple[str, str]]:
        """Return list of (source_id, display_name) tuples."""
        sources = self.get_sources()
        return [(sid, sdata.get("name", sid)) for sid, sdata in sources.items()]

    def is_source_available(self, source_id: str) -> bool:
        """Check if a source is available (its jobs_path exists and is accessible)."""
        sources = self.get_sources()
        if source_id not in sources:
            return False
        jobs_path = Path(sources[source_id]["jobs_path"])
        try:
            return jobs_path.exists() and jobs_path.is_dir()
        except (PermissionError, OSError):
            return False

    def set_source(self, source_id: str):
        """Switch to a different source and reset selections."""
        if source_id in self.config.get("sources", {}):
            self.current_source = source_id
            self.current_project = None
            self.current_sequence = None
            self.current_shot = None
            self.save_config()

    @property
    def current_source_name(self) -> str:
        """Return display name of current source."""
        sources = self.get_sources()
        if self.current_source in sources:
            return sources[self.current_source].get("name", self.current_source)
        return self.current_source

    @property
    def jobs_path(self) -> Path:
        """Return the JOBS path for current source."""
        sources = self.get_sources()
        if self.current_source in sources:
            return Path(sources[self.current_source]["jobs_path"])
        # Fallback
        return Path(list(sources.values())[0]["jobs_path"]) if sources else Path(".")

    @property
    def system_path(self) -> Path:
        """Return the SYSTEM path for current source."""
        sources = self.get_sources()
        if self.current_source in sources:
            return Path(sources[self.current_source]["system_path"])
        # Fallback
        return Path(list(sources.values())[0]["system_path"]) if sources else Path(".")

    @property
    def user_name(self) -> str:
        """Return the username from config."""
        return self.config["user_name"]

    @property
    def blender_executable(self) -> str:
        """Return the Blender executable path from config."""
        return self.config["blender_executable"]

    def _list_directories(self, path: Path) -> list[str]:
        """List directories at path, excluding hidden and special folders."""
        if not path.exists():
            return []

        dirs = []
        try:
            for entry in path.iterdir():
                if entry.is_dir():
                    name = entry.name
                    # Skip hidden folders and excluded folders
                    if not name.startswith(".") and name not in self.EXCLUDED_FOLDERS:
                        dirs.append(name)
        except PermissionError:
            return []

        return sorted(dirs)

    def projects(self) -> list[str]:
        """List available projects from JOBS path."""
        return self._list_directories(self.jobs_path)

    def sequences(self, project: Optional[str] = None) -> list[str]:
        """List sequences for a given project."""
        proj = project or self.current_project
        if not proj:
            return []
        return self._list_directories(self.jobs_path / proj)

    def shots(self, project: Optional[str] = None, sequence: Optional[str] = None) -> list[str]:
        """List shots for a given project and sequence."""
        proj = project or self.current_project
        seq = sequence or self.current_sequence
        if not proj or not seq:
            return []
        return self._list_directories(self.jobs_path / proj / seq)

    def set_project(self, project: str):
        """Set current project and reset sequence/shot."""
        self.current_project = project
        self.current_sequence = None
        self.current_shot = None
        self.save_config()

    def set_sequence(self, sequence: str):
        """Set current sequence and reset shot."""
        self.current_sequence = sequence
        self.current_shot = None
        self.save_config()

    def set_shot(self, shot: str):
        """Set current shot."""
        self.current_shot = shot
        self.save_config()

    def get_shot_path(self) -> Optional[Path]:
        """Get the full path to the current shot."""
        if not all([self.current_project, self.current_sequence, self.current_shot]):
            return None
        return self.jobs_path / self.current_project / self.current_sequence / self.current_shot

    def get_job_path(self) -> Optional[str]:
        """Get the relative job path (project/sequence/shot)."""
        if not all([self.current_project, self.current_sequence, self.current_shot]):
            return None
        return f"{self.current_project}/{self.current_sequence}/{self.current_shot}"

    def build_environment(self) -> dict[str, str]:
        """Build environment dictionary with all job-related variables.

        Based on launchPad.py:305-338 from the job's pipeline.
        """
        env = os.environ.copy()

        # Core paths
        env["JOBS"] = str(self.jobs_path)
        env["JOBROOT"] = str(self.jobs_path)
        env["SYSTEM"] = str(self.system_path)
        env["USER_NAME"] = self.user_name

        # MF Pipeline root (following job convention)
        mf_root = self.system_path / "TOOLS" / "mfpipeline" / "pipeline_v7.0.0"
        env["MF_ROOT"] = str(mf_root)

        # Job-specific variables (only if project/sequence/shot are set)
        if self.current_project:
            env["JOBPROJ"] = self.current_project

        if self.current_sequence:
            env["JOBSEQ"] = self.current_sequence

        if self.current_shot:
            env["JOBSHOT"] = self.current_shot

        # Full paths (only if all three are set)
        if all([self.current_project, self.current_sequence, self.current_shot]):
            job_path = self.get_job_path()
            shot_path = self.get_shot_path()
            env["JOBPATH"] = job_path
            env["SHOTPATH"] = str(shot_path)

        return env
