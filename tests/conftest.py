"""Pytest configuration and fixtures."""

import tempfile
import warnings
from pathlib import Path

import pytest
from pydantic_ai_backends import FilesystemBackend, StateBackend

from pydantic_deep.deps import DeepAgentDeps

# Filter out pytest assertion rewrite warnings for modules that are already imported
# These warnings occur when modules like anyio or logfire are imported before pytest
# and are harmless - they just indicate that pytest cannot rewrite those modules' assertions
warnings.filterwarnings(
    "ignore",
    message=".*Module already imported so cannot be rewritten.*",
    category=Warning,
)


@pytest.fixture
def state_backend():
    """Create a fresh StateBackend."""
    return StateBackend()


@pytest.fixture
def deps(state_backend):
    """Create default DeepAgentDeps with StateBackend."""
    return DeepAgentDeps(backend=state_backend)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def filesystem_backend(temp_dir):
    """Create a FilesystemBackend with temporary directory."""
    return FilesystemBackend(temp_dir)
