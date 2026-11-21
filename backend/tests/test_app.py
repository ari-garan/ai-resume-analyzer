from pathlib import Path
import re

from fastapi.testclient import TestClient

from app.core.frontend_build import frontend_build_is_current
from app.main import app


def test_health_endpoint_uses_response_envelope():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["statusCode"] == 200
    assert payload["status"] == "success"
    assert payload["data"]["status"] == "healthy"


def test_frontend_has_react_entry_and_vite_setup():
    frontend_root = Path(__file__).resolve().parents[2] / "frontend"
    app_source = (frontend_root / "src" / "pages" / "Analysis" / "index.tsx").read_text(encoding="utf-8")
    manifest = (frontend_root / "package.json").read_text(encoding="utf-8")
    assert "useState" in app_source
    assert '"react"' in manifest
    assert '"vite"' in manifest
    assert (frontend_root / "src" / "components" / "DocumentInput" / "index.tsx").is_file()
    assert (frontend_root / "src" / "services" / "analysisService.ts").is_file()
    assert (frontend_root / "src" / "common" / "constants.ts").is_file()


def test_frontend_proxy_targets_configured_backend_port():
    frontend_root = Path(__file__).resolve().parents[2] / "frontend"
    config = (frontend_root / "vite.config.ts").read_text(encoding="utf-8")
    assert 'port: 5173' in config
    assert 'http://127.0.0.1:8001' in config


def test_frontend_production_build_is_served_by_fastapi():
    with TestClient(app) as client:
        response = client.get("/")
        if not frontend_build_is_current():
            assert response.status_code == 503
            assert "missing or stale" in response.text
            return
        assert response.status_code == 200
        script_path = re.search(r'src="([^"]+\.js)"', response.text).group(1)
        style_path = re.search(r'href="([^"]+\.css)"', response.text).group(1)
        script = client.get(script_path)
        stylesheet = client.get(style_path)
    assert "Scoreboare" in response.text
    assert script.status_code == 200
    assert "Analysis workspace" in script.text
    assert stylesheet.status_code == 200
    assert "--canvas" in stylesheet.text
