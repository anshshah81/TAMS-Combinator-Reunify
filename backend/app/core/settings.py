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

    def __post_init__(self):
        if self.demo_auth and self.environment != 'development':
            raise ValueError('Demo authentication is permitted only in development.')
        if self.frontend_origin not in ('http://localhost:3000', 'http://127.0.0.1:3000'):
            raise ValueError('This demo only supports a loopback frontend.')

    @classmethod
    def from_env(cls):
        return cls(environment=os.getenv('APP_ENV', 'development'),
                   demo_auth=os.getenv('DEMO_AUTH_ENABLED', 'false').lower() == 'true',
                   upload_dir=Path(os.getenv('UPLOAD_DIR', str(cls.upload_dir))),
                   frontend_origin=os.getenv('FRONTEND_ORIGIN', cls.frontend_origin))
