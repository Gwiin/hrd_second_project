import { useEffect, useState, type FormEvent } from 'react';
import { IncidentResponsePanel } from './IncidentResponsePanel';
import { copyByLanguage, languageOptions, sensorIds, type Language, type QualityLabelKey, type StatusLabelKey } from './language';

type Device = {
  device_id: string;
  zone_id: string;
  device_name: string;
  model: string;
  status: string;
  protocol?: string;
  last_seen_at?: string | null;
};

type Health = {
  app: string;
  status: string;
  safety_state: string;
  uptime_seconds: number;
  last_update: string | null;
  processes: Record<string, string>;
};

type Reading = {
  site_id: string;
  zone_id: string;
  device_id: string;
  sensor_id: string;
  value: number | boolean;
  unit: string;
  timestamp: string;
  quality: string;
};

type LogEntry = {
  timestamp: string;
  level: string;
  message: string;
};

type Alert = {
  alert_id: number | null;
  level: string;
  code: string;
  message: string;
  zone_id: string | null;
  device_id: string | null;
  sensor_id: string | null;
  value: number | null;
  status: string;
  created_at: string;
};

type TimelineEntry = {
  id: string;
  type: string;
  timestamp: string;
  title: string;
  message: string;
  tone: string;
  zone_id?: string | null;
  device_id?: string | null;
  sensor_id?: string | null;
  process?: string;
  status?: string;
  quality?: string;
};

type ProcessLiveness = {
  kind: 'process';
  process: string;
  status: string;
  last_seen_at: string | null;
};

type DeviceLiveness = Device & {
  kind: 'device';
};

type Liveness = {
  devices: DeviceLiveness[];
  processes: ProcessLiveness[];
};

type LatestReadings = Record<string, Record<string, Reading>>;
type RealtimeState = 'live' | 'reconnecting' | 'offline';

type RealtimeMessage = {
  type: 'reading.created';
  reading: Reading;
};

type AuthMode = 'signin' | 'signup';
type AuthProvider = 'google' | 'kakao';
type AuthErrorKey = 'signupError' | 'signinError';

type User = {
  user_id: number;
  email: string;
  display_name: string;
  provider: string;
};

type SessionResponse = {
  authenticated: boolean;
  user: User | null;
};

type AuthResponse = {
  user: User;
};

const fallbackDevices: Device[] = [
  { device_id: 'pico-safe-001', zone_id: 'room-1', device_name: 'Pico Safe 001', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-002', zone_id: 'room-2', device_name: 'Pico Safe 002', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-003', zone_id: 'room-3', device_name: 'Pico Safe 003', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-004', zone_id: 'room-4', device_name: 'Pico Safe 004', model: 'Raspberry Pi Pico 2W', status: 'online' }
];

const fallbackHealth: Health = {
  app: 'Pico SafeRoom',
  status: 'starting',
  safety_state: 'safe',
  uptime_seconds: 0,
  last_update: null,
  processes: {
    backend: 'connecting',
    collector: 'offline',
    worker: 'offline'
  }
};

const fallbackLiveness: Liveness = {
  devices: fallbackDevices.map((device) => ({ ...device, kind: 'device' })),
  processes: [
    { kind: 'process', process: 'backend', status: 'connecting', last_seen_at: null },
    { kind: 'process', process: 'collector', status: 'connecting', last_seen_at: null },
    { kind: 'process', process: 'worker', status: 'connecting', last_seen_at: null }
  ]
};

function formatTime(value: string | null): string {
  if (!value) return '--:--:--';
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatUptime(seconds: number): string {
  const hours = Math.floor(seconds / 3600).toString().padStart(2, '0');
  const minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
  const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${hours}:${minutes}:${secs}`;
}

function formatReading(reading: Reading | undefined, sensorId: string, motion: string, noMotion: string): string {
  if (!reading) return '--';
  if (sensorId === 'motion') return reading.value ? motion : noMotion;
  return `${reading.value} ${reading.unit === 'celsius' ? 'C' : reading.unit}`;
}

function sensorQuality(reading: Reading | undefined): string {
  if (!reading) return 'missing';
  const timestampMs = new Date(reading.timestamp).getTime();
  if (Number.isFinite(timestampMs) && Date.now() - timestampMs > 30_000) return 'stale';
  return reading.quality;
}

function qualityTone(quality: string): string {
  if (quality === 'bad' || quality === 'missing') return 'critical';
  if (quality === 'stale' || quality === 'uncertain') return 'warning';
  return 'safe';
}

function sparkline(seed: number): string {
  return Array.from({ length: 20 }, (_, index) => {
    const x = 5 + index * 8;
    const y = 32 - (Math.sin(index / 2 + seed) * 7 + Math.cos(index / 3 + seed) * 4);
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ');
}

function statusTone(status: string): string {
  if (status === 'critical' || status === 'offline' || status === 'bad' || status === 'missing') return 'critical';
  if (status === 'warning' || status === 'degraded' || status === 'simulated' || status === 'stale') return 'warning';
  return 'safe';
}

function formatStatusLabel(status: string, labels: Record<StatusLabelKey, string>): string {
  return labels[status as StatusLabelKey] ?? status;
}

function formatQualityLabel(quality: string, labels: Record<QualityLabelKey, string>): string {
  return labels[quality as QualityLabelKey] ?? quality;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>('signin');
  const [authErrorKey, setAuthErrorKey] = useState<AuthErrorKey | null>(null);
  const [authBusy, setAuthBusy] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [devices, setDevices] = useState<Device[]>(fallbackDevices);
  const [selectedDeviceId, setSelectedDeviceId] = useState('pico-safe-001');
  const [health, setHealth] = useState<Health>(fallbackHealth);
  const [readings, setReadings] = useState<LatestReadings>({});
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [liveness, setLiveness] = useState<Liveness>(fallbackLiveness);
  const [realtimeState, setRealtimeState] = useState<RealtimeState>('reconnecting');

  useEffect(() => {
    let cancelled = false;

    async function loadSession() {
      const response = await fetch('/api/auth/me', { credentials: 'include' });
      if (!response.ok || cancelled) return;
      const session: SessionResponse = await response.json();
      if (!cancelled) {
        setIsAuthenticated(Boolean(session.authenticated));
        setCurrentUser(session.user);
      }
    }

    loadSession().catch(() => undefined);

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      const [
        healthResponse,
        devicesResponse,
        readingsResponse,
        logsResponse,
        alertsResponse,
        timelineResponse,
        livenessResponse
      ] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/devices'),
        fetch('/api/readings/latest'),
        fetch('/api/logs'),
        fetch('/api/alerts'),
        fetch('/api/timeline?limit=12'),
        fetch('/api/liveness')
      ]);
      if (cancelled) return;
      setHealth(await healthResponse.json());
      setDevices((await devicesResponse.json()).devices);
      setReadings((await readingsResponse.json()).readings);
      setLogs((await logsResponse.json()).logs);
      setAlerts((await alertsResponse.json()).alerts);
      setTimeline((await timelineResponse.json()).events);
      setLiveness(await livenessResponse.json());
    }

    refresh().catch(() => undefined);
    const interval = window.setInterval(() => {
      refresh().catch(() => undefined);
    }, 2500);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let stopped = false;

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      socket = new WebSocket(`${protocol}://${window.location.host}/ws/realtime`);

      socket.onopen = () => {
        setRealtimeState('live');
      };

      socket.onmessage = (event) => {
        const message = JSON.parse(event.data) as RealtimeMessage;
        if (message.type !== 'reading.created') return;
        const reading = message.reading;
        setReadings((current) => ({
          ...current,
          [reading.device_id]: {
            ...(current[reading.device_id] ?? {}),
            [reading.sensor_id]: reading
          }
        }));
        setHealth((current) => ({
          ...current,
          last_update: new Date().toISOString()
        }));
      };

      socket.onclose = () => {
        if (stopped) return;
        setRealtimeState('reconnecting');
        reconnectTimer = window.setTimeout(connect, 1500);
      };

      socket.onerror = () => {
        setRealtimeState('offline');
        socket?.close();
      };
    }

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  const selectedDevice = devices.find((device) => device.device_id === selectedDeviceId) ?? devices[0];
  const selectedReadings = readings[selectedDevice?.device_id] ?? {};
  const safetyTone = statusTone(health.safety_state);
  const copy = copyByLanguage[language];

  const timelineRows = timeline.length
    ? timeline
    : [{
      id: 'waiting',
      type: 'log',
      timestamp: new Date().toISOString(),
      title: 'waiting',
      message: copy.app.waitingForMqtt,
      tone: 'warning'
    }];
  const livenessDevices = liveness.devices.length ? liveness.devices : fallbackLiveness.devices;
  const livenessProcesses = liveness.processes.length ? liveness.processes : fallbackLiveness.processes;

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setAuthErrorKey(null);

    const form = new FormData(event.currentTarget);
    const payload = {
      email: String(form.get('email') ?? ''),
      password: String(form.get('password') ?? '')
    };
    const response = authMode === 'signup'
      ? await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      })
      : await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

    setAuthBusy(false);

    if (!response.ok) {
      setAuthErrorKey(authMode === 'signup' ? 'signupError' : 'signinError');
      return;
    }

    const authResult: AuthResponse = await response.json();
    setCurrentUser(authResult.user);
    setIsAuthenticated(true);
  }

  function handleSocialAuth(provider: AuthProvider) {
    window.location.href = `/api/auth/social/${provider}/start`;
  }

  async function handleLogout() {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    }).catch(() => undefined);
    setIsAuthenticated(false);
    setCurrentUser(null);
  }

  function renderLanguageToggle(className = '') {
    return (
      <div className={`language-toggle ${className}`} aria-label={copy.app.language}>
        {languageOptions.map((option) => (
          <button
            className={language === option.id ? 'active' : ''}
            key={option.id}
            type="button"
            onClick={() => setLanguage(option.id)}
          >
            {option.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <main className="app-shell">
      <div className={isAuthenticated ? 'dashboard-shell' : 'dashboard-shell auth-locked'} aria-hidden={!isAuthenticated}>
        <header className="topbar">
          <div className="brand">
            <span className="brand-status" aria-hidden="true" />
            <div>
              <h1>Pico SafeRoom</h1>
              <span>{copy.app.subtitle}</span>
            </div>
            {isAuthenticated && (
              <button className="sign-out-button" type="button" onClick={handleLogout}>
                {copy.app.signOut}
              </button>
            )}
          </div>
          {isAuthenticated && currentUser && (
            <div className="user-info">
              <span>{copy.app.signedInAs}</span>
              <strong>{currentUser.display_name}</strong>
              <small>{currentUser.email}</small>
              <em>{copy.app.authProvider}: {currentUser.provider}</em>
            </div>
          )}
          {renderLanguageToggle()}
          <div className={`safety ${safetyTone}`}>
            <span>{copy.app.safetyState}</span>
            <strong>{formatStatusLabel(health.safety_state, copy.statusLabels)}</strong>
          </div>
          {Object.entries(health.processes).map(([name, state]) => (
            <div className="process" key={name}>
              <span>{name}</span>
              <strong><i className={statusTone(state)} />{formatStatusLabel(state, copy.statusLabels)}</strong>
            </div>
          ))}
          <div className="timebox">
            <span>{copy.app.uptime}</span>
            <strong>{formatUptime(health.uptime_seconds)}</strong>
          </div>
          <div className="timebox">
            <span>{copy.app.lastUpdate}</span>
            <strong>{formatTime(health.last_update)}</strong>
          </div>
          <div className={`realtime ${realtimeState}`}>
            <span>{copy.app.realtime}</span>
            <strong><i />{formatStatusLabel(realtimeState, copy.statusLabels)}</strong>
          </div>
        </header>

        <section className="workspace">
          <aside className="sidebar">
            <h2>{copy.app.zones}</h2>
            <div className="zone-list">
              {devices.map((device) => (
                <button
                  className={device.device_id === selectedDeviceId ? 'zone active' : 'zone'}
                  key={device.device_id}
                  onClick={() => setSelectedDeviceId(device.device_id)}
                >
                  <span>{device.zone_id.replace('-', ' ')}</span>
                  <small>{device.device_id}</small>
                  <i className={statusTone(device.status)} />
                </button>
              ))}
            </div>
            <h2>{copy.app.devices}</h2>
            <div className="device-card">
              <strong>{selectedDevice?.device_id}</strong>
              <span>{selectedDevice?.model}</span>
            </div>
          </aside>

          <section className="dashboard">
            <section className="panel">
              <div className="panel-title">
                <h2>{copy.app.latestReadings}</h2>
                <span>{selectedDevice?.zone_id} / {selectedDevice?.device_id}</span>
              </div>
              <div className="reading-grid">
                {sensorIds.map((sensorId, index) => {
                  const reading = selectedReadings[sensorId];
                  const quality = sensorQuality(reading);
                  const tone = qualityTone(quality);
                  return (
                    <article className={`reading-card ${tone}`} key={sensorId}>
                      <span className="sensor-name">{copy.sensors[sensorId]}</span>
                      <strong>{formatReading(reading, sensorId, copy.app.motion, copy.app.noMotion)}</strong>
                      <small className={`quality-badge ${tone}`}>{formatQualityLabel(quality, copy.qualityLabels)}</small>
                      <svg viewBox="0 0 170 44" aria-hidden="true">
                        <path d={sparkline(index + selectedDeviceId.length)} />
                      </svg>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="panel timeline-panel">
              <div className="panel-title">
                <h2>{copy.app.blackboxTimeline}</h2>
                <span>{realtimeState === 'live' ? copy.app.liveFlow : copy.app.restPolling}</span>
              </div>
              <div className="blackbox-list">
                {timelineRows.slice(0, 9).map((entry) => (
                  <article className={`blackbox-event ${statusTone(entry.tone)}`} key={entry.id}>
                    <time>{formatTime(entry.timestamp)}</time>
                    <i />
                    <div>
                      <strong>{entry.title}</strong>
                      <span>{entry.message}</span>
                    </div>
                    <em>{entry.type.replace('_', ' ')}</em>
                  </article>
                ))}
              </div>
            </section>
          </section>

          <aside className="right-rail">
            <IncidentResponsePanel
              alerts={alerts}
              copy={copy.incident}
              fallbackZone={selectedDevice?.zone_id ?? 'room-1'}
              formatTime={formatTime}
              statusLabels={copy.statusLabels}
              statusTone={statusTone}
            />
            <section className="panel liveness-panel">
              <h2>{copy.app.liveness}</h2>
              <div className="liveness-group">
                <span>{copy.app.devices}</span>
                {livenessDevices.map((device) => (
                  <div className="liveness-row" key={device.device_id}>
                    <i className={statusTone(device.status)} />
                    <strong>{device.device_id}</strong>
                    <em>{formatStatusLabel(device.status, copy.statusLabels)}</em>
                  </div>
                ))}
              </div>
              <div className="liveness-group">
                <span>{copy.app.processes}</span>
                {livenessProcesses.map((process) => (
                  <div className="liveness-row" key={process.process}>
                    <i className={statusTone(process.status)} />
                    <strong>{process.process}</strong>
                    <em>{formatStatusLabel(process.status, copy.statusLabels)}</em>
                  </div>
                ))}
              </div>
            </section>
            <section className="panel logs">
              <h2>{copy.app.systemLog}</h2>
              {(logs.length ? logs : [{ timestamp: new Date().toISOString(), level: 'info', message: copy.app.waitingForCollector }]).slice(0, 6).map((log, index) => (
                <div className="log-row" key={`${log.timestamp}-${index}`}>
                  <span>{formatTime(log.timestamp)}</span>
                  <i />
                  <p>{log.message}</p>
                </div>
              ))}
            </section>
          </aside>
        </section>

        <footer className="footer">
          <span><strong>{copy.app.lastEvent}:</strong> {logs[0]?.message ?? copy.app.waitingForReadings}</span>
          <span><strong>{copy.app.runtime}:</strong> {formatUptime(health.uptime_seconds)}</span>
          <span><strong>{copy.app.dataFlow}:</strong> {realtimeState === 'live' ? 'websocket' : 'REST'}</span>
          <span><strong>{copy.app.localTime}:</strong> {new Date().toLocaleTimeString()}</span>
        </footer>
      </div>

      {!isAuthenticated && (
        <section className="auth-backdrop" role="dialog" aria-modal="true" aria-labelledby="auth-title">
          <div className="auth-context">
            <span>{copy.auth.realBoardMode}</span>
            <strong>{copy.auth.protectedDevices}</strong>
            <p>{copy.auth.description}</p>
          </div>

          <form className="auth-card" onSubmit={handleAuthSubmit}>
            {renderLanguageToggle('auth-language')}
            <div className="auth-header">
              <span className="brand-status" aria-hidden="true" />
              <div>
                <h2 id="auth-title">Pico SafeRoom</h2>
                <p>{copy.auth.subtitle}</p>
              </div>
            </div>

            <div className="auth-tabs" aria-label={copy.auth.modeLabel}>
              <button
                type="button"
                className={authMode === 'signin' ? 'active' : ''}
                onClick={() => setAuthMode('signin')}
              >
                {copy.auth.signIn}
              </button>
              <button
                type="button"
                className={authMode === 'signup' ? 'active' : ''}
                onClick={() => setAuthMode('signup')}
              >
                {copy.auth.createAccount}
              </button>
            </div>

            <div className="social-auth">
              <button type="button" onClick={() => handleSocialAuth('google')}>
                <i className="google-dot" aria-hidden="true" />
                {copy.auth.continueGoogle}
              </button>
              <button type="button" onClick={() => handleSocialAuth('kakao')}>
                <i className="kakao-dot" aria-hidden="true" />
                {copy.auth.continueKakao}
              </button>
            </div>

            <div className="auth-divider"><span>{copy.auth.email}</span></div>

            <label>
              <span>{copy.auth.email}</span>
              <input type="email" name="email" autoComplete="email" required />
            </label>
            <label>
              <span>{copy.auth.password}</span>
              <input
                type="password"
                name="password"
                autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'}
                required
              />
            </label>
            {authErrorKey && <p className="auth-error">{copy.auth[authErrorKey]}</p>}
            <button className="auth-submit" type="submit">
              {authBusy ? copy.auth.checking : authMode === 'signup' ? copy.auth.createAccount : copy.auth.signIn}
            </button>
          </form>
        </section>
      )}
    </main>
  );
}
