from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_TSX = ROOT / "frontend" / "src" / "App.tsx"
APP_CSS = ROOT / "frontend" / "src" / "App.css"


def test_pre_login_dashboard_is_blurred_and_locked():
    app = APP_TSX.read_text()
    css = APP_CSS.read_text()

    assert "auth-locked" in app
    assert "auth-backdrop" in app
    assert "aria-hidden={!isAuthenticated}" in app
    assert "filter: blur(14px)" in css
    assert "pointer-events: none" in css


def test_auth_gate_offers_social_and_email_entry_points():
    app = APP_TSX.read_text()

    assert "Continue with Google" in app
    assert "Continue with Apple" in app
    assert "Continue with Kakao" in app
    assert "Create account" in app
    assert 'type="email"' in app
    assert 'type="password"' in app


def test_auth_gate_uses_backend_auth_endpoints():
    app = APP_TSX.read_text()

    assert "fetch('/api/auth/me'" in app
    assert "fetch('/api/auth/signup'" in app
    assert "fetch('/api/auth/login'" in app
    assert "window.location.href = `/api/auth/social/${provider}/start`" in app


def test_authenticated_dashboard_has_logout_action():
    app = APP_TSX.read_text()

    assert "Sign out" in app
    assert "fetch('/api/auth/logout'" in app
    assert "setIsAuthenticated(false)" in app
