"""Phase 4 tests: clothing detection mock adapter, structured contract,
non-detection vs error semantics, and the protected endpoint. No weights."""
import pytest

from app.services.ai import clothing_detection as cd
from app.services.ai.clothing_detection import (ClothingDetectionUnavailable, MockClothingDetector,
                                                 detect_clothing, get_detector)

from test_intake import CSRF, build, make_client, png_bytes  # shared Phase 2 harness

DESCRIPTIONS = ['red hoodie', 'blue jeans', 'white sneakers']


def write(path, data: bytes):
    path.write_bytes(data)
    return str(path)


def test_detection_contract_and_support(tmp_path):
    image = write(tmp_path / 'p.png', png_bytes())
    result = detect_clothing(image, DESCRIPTIONS)
    assert result.status in (cd.STATUS_DETECTED, cd.STATUS_NONE_DETECTED)
    assert result.mock is True
    assert [q.query for q in result.queries] == DESCRIPTIONS
    # Person-association reminder is always surfaced.
    assert 'associate clothing' in (result.warning or '').lower()
    for query in result.queries:
        if query.supported:
            assert query.detections and 0.0 <= query.detections[0].score <= 1.0
            box = query.detections[0].box
            assert len(box) == 4 and all(0.0 <= value <= 1.0 for value in box)
            assert 'color' in (query.note or '').lower()
        else:
            assert query.detections == []
            assert 'absent' in (query.note or '').lower()


def test_detection_is_deterministic(tmp_path):
    image = write(tmp_path / 'p.png', png_bytes())
    first = detect_clothing(image, DESCRIPTIONS).as_dict()
    second = detect_clothing(image, DESCRIPTIONS).as_dict()
    assert first == second


def test_missing_image_and_empty_descriptions_error(tmp_path):
    good = write(tmp_path / 'p.png', png_bytes())
    assert detect_clothing(str(tmp_path / 'nope.png'), DESCRIPTIONS).status == cd.STATUS_ERROR
    assert detect_clothing(good, []).status == cd.STATUS_ERROR
    bad = write(tmp_path / 'bad.png', b'nope')
    assert detect_clothing(bad, DESCRIPTIONS).status == cd.STATUS_ERROR


def test_detector_selection():
    assert isinstance(get_detector('mock'), MockClothingDetector)
    with pytest.raises(ValueError):
        get_detector('unknown')
    with pytest.raises(ClothingDetectionUnavailable):
        get_detector('grounding_dino')


def _upload(app) -> str:
    hospital = make_client(app, 'hospital-demo')
    return hospital.post('/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')},
                         headers=CSRF).json()['image_id']


def test_reviewer_can_request_clothing_detection(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        image_id = _upload(app)
        reviewer = make_client(app, 'reviewer-demo')
        response = reviewer.post('/api/v1/clothing-detections',
                                 json={'image_id': image_id, 'clothing_descriptions': DESCRIPTIONS}, headers=CSRF)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body['mock'] is True and len(body['queries']) == 3
    finally:
        engine.dispose()


def test_clothing_detection_rejects_family_and_bad_input(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        image_id = _upload(app)
        family = make_client(app, 'family-demo')
        assert family.post('/api/v1/clothing-detections',
                           json={'image_id': image_id, 'clothing_descriptions': DESCRIPTIONS}, headers=CSRF).status_code == 403
        reviewer = make_client(app, 'reviewer-demo')
        assert reviewer.post('/api/v1/clothing-detections',
                             json={'image_id': image_id, 'clothing_descriptions': []}, headers=CSRF).status_code == 422
        assert reviewer.post('/api/v1/clothing-detections',
                             json={'image_id': 'a' * 32, 'clothing_descriptions': DESCRIPTIONS}, headers=CSRF).status_code == 404
    finally:
        engine.dispose()
