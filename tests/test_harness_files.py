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
    ROOT / "docs" / "agents" / "ci-tests-plan.md",
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
    assert "bootstrap-harness:" in content
    assert "check:" in content
    assert "test:" in content
    assert "verify:" in content



def test_agent_docs_readme_mentions_all_agent_docs():
    docs_dir = ROOT / "docs" / "agents"
    readme = (docs_dir / "README.md").read_text()
    documented = {
        line.split("`")[1]
        for line in readme.splitlines()
        if line.strip().startswith("- `") and line.count("`") >= 2
    }
    actual = {path.name for path in docs_dir.glob("*.md") if path.name != "README.md"}
    missing = sorted(actual - documented)
    assert not missing, f"docs/agents/README.md is missing entries for: {missing}"



def test_harness_workflow_uses_documented_bootstrap_and_verify_loop():
    content = (ROOT / ".github" / "workflows" / "harness.yml").read_text()
    assert "make bootstrap-harness" in content
    assert "make verify" in content
