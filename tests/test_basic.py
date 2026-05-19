"""
Basic smoke tests for Hutchinson Synthesis.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hutchinson_pure'))


def test_imports():
    import gigp
    import niche
    import score_generator
    import renderer
    print("All imports OK")


def test_gigp_sampling():
    from gigp import sample_gigp
    # Basic smoke test: should return a list of points
    points = sample_gigp(n_events=10, beta=0.0, kernel='gaussian', sigma=0.3)
    assert len(points) == 10
    print(f"GIGP sampling OK: {len(points)} events")


if __name__ == '__main__':
    test_imports()
    test_gigp_sampling()
    print("All tests passed.")
