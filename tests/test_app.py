import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.outline_optimizer import optimize_outline
from core.draft_optimizer import optimize_draft

def test_outline_optimizer():
    """Test outline optimization with sample inputs."""
    sample_report = """
# Sample Query Fan-Out
## Sub-Queries
- Test sub-query 1
- Test sub-query 2

## Insights
- Add more coverage
"""
    sample_outline = """
# Test Outline
## Section 1
- Point 1
"""
    try:
        result, metadata = optimize_outline(sample_report, sample_outline)
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'intent' in metadata
        print("Outline test passed.")
    except Exception as e:
        pytest.fail(f"Outline optimization failed: {e}")

def test_draft_optimizer():
    """Test draft optimization with sample inputs."""
    sample_draft = "This is a sample draft about testing."
    sample_keywords = "test keyword, sample"
    try:
        result, metadata = optimize_draft(sample_draft, sample_keywords)
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'top_keywords' in metadata
        print("Draft test passed.")
    except Exception as e:
        pytest.fail(f"Draft optimization failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])