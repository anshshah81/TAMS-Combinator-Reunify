import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    environment: str = 'development'
    demo_auth: bool = False
    frontend_origin: str = 'http://localhost:3000'
    upload_dir: Path = Path(__file__).resolve().parents[2] / 'uploads'
    session_seconds: int = 3600
    max_image_bytes: int = 5 * 1024 * 1024
    # Facial similarity runs in labeled mock mode by default. 'arcface' opts into
    # real DeepFace/ArcFace inference and requires the optional AI dependencies.
    face_match_mode: str = 'mock'
    # Clothing detection likewise defaults to a labeled mock; 'grounding_dino'
    # opts into real inference with the optional AI dependencies.
    clothing_detect_mode: str = 'mock'

    def __post_init__(self):
        if self.demo_auth and self.environment != 'development':
            raise ValueError('Demo authentication is permitted only in development.')
        if self.frontend_origin not in ('http://localhost:3000', 'http://127.0.0.1:3000'):
            raise ValueError('This demo only supports a loopback frontend.')
        if self.face_match_mode not in ('mock', 'arcface'):
            raise ValueError('FACE_MATCH_MODE must be "mock" or "arcface".')
        if self.clothing_detect_mode not in ('mock', 'grounding_dino'):
            raise ValueError('CLOTHING_DETECT_MODE must be "mock" or "grounding_dino".')

    @classmethod
    def from_env(cls):
        return cls(environment=os.getenv('APP_ENV', 'development'),
                   demo_auth=os.getenv('DEMO_AUTH_ENABLED', 'false').lower() == 'true',
                   upload_dir=Path(os.getenv('UPLOAD_DIR', str(cls.upload_dir))),
                   frontend_origin=os.getenv('FRONTEND_ORIGIN', cls.frontend_origin),
                   face_match_mode=os.getenv('FACE_MATCH_MODE', cls.face_match_mode),
                   clothing_detect_mode=os.getenv('CLOTHING_DETECT_MODE', cls.clothing_detect_mode))
