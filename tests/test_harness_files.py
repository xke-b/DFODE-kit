from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "Makefile",
    ROOT / "pytest.ini",
    ROOT / "docs" / "agents" / "README.md",
    ROOT / "docs" / "agents" / "verification.md",
    ROOT / "docs" / "agents" / "worktrees.md",
    ROOT / "docs" / "agents" / "roadmap.md",
    ROOT / "docs" / "agents" / "topology.md",
]


def test_required_harness_files_exist():
    missing = [path for path in REQUIRED_FILES if not path.exists()]
    assert not missing, f"Missing harness files: {missing}"


def test_agents_md_references_deeper_docs():
    content = (ROOT / "AGENTS.md").read_text()
    assert "docs/agents/verification.md" in content
    assert "docs/agents/worktrees.md" in content


def test_makefile_has_verification_targets():
    content = (ROOT / "Makefile").read_text()
    assert "check:" in content
    assert "test:" in content
    assert "verify:" in content
