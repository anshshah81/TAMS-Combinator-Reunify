"""Phase 3 tests: facial similarity mock adapter, structured contract, error
handling, and the protected comparison endpoint. No model weights are downloaded."""
import pytest

from app.services.ai.face_matching import (FaceMatchingUnavailable, MockFaceMatcher,
                                           compare_faces, get_matcher)
from app.services.ai import face_matching

from test_intake import CSRF, build, make_client, png_bytes  # shared Phase 2 harness


def write(path, data: bytes):
    path.write_bytes(data)
    return str(path)


def test_identical_images_have_zero_distance(tmp_path):
    same = png_bytes()
    a = write(tmp_path / 'a.png', same)
    b = write(tmp_path / 'b.png', same)
    result = compare_faces(a, b)
    assert result.status == face_matching.STATUS_COMPARED
    assert result.distance == 0.0
    assert result.mock is True
    assert result.model == 'ArcFace (mock)' and result.detector == 'mock'
    assert set(result.as_dict()) == {'status', 'distance', 'model', 'detector', 'warning', 'mock'}


def test_different_images_have_positive_distance(tmp_path):
    a = write(tmp_path / 'a.png', png_bytes((255, 0, 0)))
    b = write(tmp_path / 'b.png', png_bytes((0, 0, 255)))
    result = compare_faces(a, b)
    assert result.status == face_matching.STATUS_COMPARED
    assert result.distance is not None and 0.0 < result.distance < 1.0


def test_missing_and_invalid_images_report_error(tmp_path):
    good = write(tmp_path / 'a.png', png_bytes())
    missing = compare_faces(good, str(tmp_path / 'nope.png'))
    assert missing.status == face_matching.STATUS_ERROR and missing.distance is None
    bad = write(tmp_path / 'bad.png', b'not an image')
    invalid = compare_faces(good, bad)
    assert invalid.status == face_matching.STATUS_ERROR and invalid.distance is None


def test_matcher_selection():
    assert isinstance(get_matcher('mock'), MockFaceMatcher)
    with pytest.raises(ValueError):
        get_matcher('unknown')
    # Real adapter is opt-in; without optional deps it raises rather than faking.
    with pytest.raises(FaceMatchingUnavailable):
        get_matcher('arcface')


# --- Endpoint -----------------------------------------------------------------

def _two_images(app):
    family = make_client(app, 'family-demo')
    hospital = make_client(app, 'hospital-demo')
    ref = family.post('/api/v1/images', files={'file': ('r.png', png_bytes((255, 0, 0)), 'image/png')},
                      headers=CSRF).json()['image_id']
    cand = hospital.post('/api/v1/images', files={'file': ('c.png', png_bytes((0, 0, 255)), 'image/png')},
                         headers=CSRF).json()['image_id']
    return ref, cand


def test_reviewer_can_request_face_comparison(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        ref, cand = _two_images(app)
        reviewer = make_client(app, 'reviewer-demo')
        response = reviewer.post('/api/v1/face-comparisons',
                                 json={'reference_image_id': ref, 'candidate_image_id': cand}, headers=CSRF)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body['status'] == 'compared' and body['mock'] is True
        assert body['distance'] is not None
    finally:
        engine.dispose()


def test_family_cannot_request_face_comparison(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        ref, cand = _two_images(app)
        family = make_client(app, 'family-demo')
        response = family.post('/api/v1/face-comparisons',
                               json={'reference_image_id': ref, 'candidate_image_id': cand}, headers=CSRF)
        assert response.status_code == 403
    finally:
        engine.dispose()


def test_face_comparison_unknown_image_is_404(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        reviewer = make_client(app, 'reviewer-demo')
        missing = 'a' * 32
        response = reviewer.post('/api/v1/face-comparisons',
                                 json={'reference_image_id': missing, 'candidate_image_id': missing}, headers=CSRF)
        assert response.status_code == 404
    finally:
        engine.dispose()
