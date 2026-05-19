"""Basic smoke tests for Hutchinson Synthesis."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

def test_imports():
    import gigp
    print("Import OK")

def test_gigp_sampling():
    from gigp import sample_gigp
    points = sample_gigp(n_events=10, beta=0.0, kernel='gaussian', sigma=0.3)
    assert len(points) == 10
    print(f"GIGP sampling OK: {len(points)} events")

if __name__ == '__main__':
    test_imports()
    test_gigp_sampling()
    print("All tests passed.")
