from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_TSX = ROOT / "frontend" / "src" / "App.tsx"
INCIDENT_PANEL_TSX = ROOT / "frontend" / "src" / "IncidentResponsePanel.tsx"
LANGUAGE_TS = ROOT / "frontend" / "src" / "language.ts"
APP_CSS = ROOT / "frontend" / "src" / "App.css"


def source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontend_source() -> str:
    incident_panel = source_text(INCIDENT_PANEL_TSX) if INCIDENT_PANEL_TSX.exists() else ""
    language = source_text(LANGUAGE_TS) if LANGUAGE_TS.exists() else ""
    return source_text(APP_TSX) + "\n" + incident_panel + "\n" + language


def test_pre_login_dashboard_is_blurred_and_locked():
    app = source_text(APP_TSX)
    css = source_text(APP_CSS)

    assert "auth-locked" in app
    assert "auth-backdrop" in app
    assert "aria-hidden={!isAuthenticated}" in app
    assert "filter: blur(14px)" in css
    assert "pointer-events: none" in css


def test_auth_gate_offers_social_and_email_entry_points():
    app = frontend_source()

    assert "Continue with Google" in app
    assert "Continue with Kakao" in app
    assert "Create account" in app
    assert 'type="email"' in app
    assert 'type="password"' in app


def test_auth_gate_uses_backend_auth_endpoints():
    app = source_text(APP_TSX)

    assert "fetch('/api/auth/me'" in app
    assert "fetch('/api/auth/signup'" in app
    assert "fetch('/api/auth/login'" in app
    assert "window.location.href = `/api/auth/social/${provider}/start`" in app


def test_authenticated_dashboard_has_logout_action():
    app = frontend_source()

    assert "Sign out" in app
    assert "fetch('/api/auth/logout'" in app
    assert "setIsAuthenticated(false)" in app


def test_dashboard_has_incident_response_workflow_hooks():
    app = frontend_source()

    assert "Incident response" in app
    assert "Replay incident" in app
    assert "Response note" in app
    assert "Evidence" in app
    assert "not replayable" in app


def test_dashboard_uses_incident_replay_and_ack_endpoints():
    app = frontend_source()

    assert "fetch(`/api/alerts/${alertId}/replay`" in app
    assert "fetch(`/api/alerts/${alertId}/ack`" in app


def test_incident_response_panel_surfaces_command_report():
    app = frontend_source()

    assert "Incident report" in app
    assert "Next action" in app
    assert "Checklist complete" in app
    assert "fetch(`/api/alerts/${alertId}/report`" in app


def test_dashboard_fetches_statistics_endpoint():
    app = source_text(APP_TSX)

    assert "fetch('/api/stats')" in app


def test_dashboard_has_statistics_navigation_and_llm_context_preview():
    app = frontend_source()

    assert "activeView" in app
    assert "setActiveView('statistics')" in app
    assert "Statistics" in app
    assert "LLM context preview" in app
    assert "/api/chat" not in app
    assert "chat input" not in app.lower()


def test_dashboard_has_korean_statistics_copy():
    app = frontend_source()

    assert "통계" in app
    assert "LLM 분석 컨텍스트" in app
    assert "총 센서값" in app


def test_statistics_page_has_environment_graphs():
    app = frontend_source()

    assert "environmentSensors" in app
    assert "renderEnvironmentOverview" in app
    assert "renderTrendPath" in app
    assert "Environment by room" in app
    assert "Recent environment trend" in app
    assert "방별 환경" in app
    assert "최근 환경 추이" in app


def test_dashboard_has_llm_placeholder_without_real_chat_integration():
    app = frontend_source()

    assert "renderLlmPlaceholder" in app
    assert "LLM assistant preview" in app
    assert "통계 기반 LLM 상담 준비 중" in app
    assert "placeholder-chat-input" in app
    assert "/api/chat" not in app
    assert "OPENAI" not in app
    assert "api key" not in app.lower()
    assert "model selector" not in app.lower()


def test_dashboard_has_english_korean_language_toggle():
    app = frontend_source()

    assert "type Language = 'en' | 'ko'" in app
    assert "languageOptions" in app
    assert "English" in app
    assert "한국어" in app
    assert "setLanguage(option.id)" in app


def test_dashboard_has_korean_copy_for_core_surfaces():
    app = frontend_source()

    assert "안전 상태" in app
    assert "최신 센서값" in app
    assert "대시보드를 열려면 로그인하세요." in app
    assert "시스템 로그" in app


def test_incident_response_panel_uses_translated_copy():
    app = frontend_source()

    assert "IncidentCopy" in app
    assert "copy={copy.incident}" in app
    assert "Incident 대응" in app
    assert "재생 타임라인" in app


def test_authenticated_dashboard_displays_logged_in_user_information():
    app = frontend_source()

    assert "type User =" in app
    assert "setCurrentUser(session.user)" in app
    assert "setCurrentUser(authResult.user)" in app
    assert "currentUser.email" in app
    assert "currentUser.display_name" in app
    assert "currentUser.provider" in app
    assert "Signed in as" in app
    assert "로그인 사용자" in app


def test_auth_errors_render_from_current_language_copy():
    app = frontend_source()

    assert "type AuthErrorKey = 'signupError' | 'signinError'" in app
    assert "setAuthErrorKey(authMode === 'signup' ? 'signupError' : 'signinError')" in app
    assert "{authErrorKey && <p className=\"auth-error\">{copy.auth[authErrorKey]}</p>}" in app
    assert "setAuthError(copy.auth" not in app


def test_incident_status_messages_render_from_current_language_copy():
    app = frontend_source()

    assert "type IncidentMessageKey = 'replayUnavailable' | 'saveFailed' | 'saved'" in app
    assert "setMessageKey('replayUnavailable')" in app
    assert "setMessageKey('saveFailed')" in app
    assert "setMessageKey('saved')" in app
    assert "{messageKey && <small>{copy[messageKey]}</small>}" in app


def test_finite_statuses_and_quality_labels_use_language_copy():
    app = frontend_source()

    assert "statusLabels" in app
    assert "qualityLabels" in app
    assert "formatStatusLabel" in app
    assert "formatQualityLabel" in app
    assert "위험" in app
    assert "정보" in app
    assert "온라인" in app
    assert "시뮬레이션" in app
    assert "정상" in app
    assert "누락" in app
    assert "statusLabels={copy.statusLabels}" in app
