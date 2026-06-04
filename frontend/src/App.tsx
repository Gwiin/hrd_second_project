import { useEffect, useState, type FormEvent } from 'react';
import { IncidentResponsePanel } from './IncidentResponsePanel';

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

const fallbackDevices: Device[] = [
  { device_id: 'pico-safe-001', zone_id: 'room-1', device_name: 'Pico Safe 001', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-002', zone_id: 'room-2', device_name: 'Pico Safe 002', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-003', zone_id: 'room-3', device_name: 'Pico Safe 003', model: 'Raspberry Pi Pico 2W', status: 'online' },
  { device_id: 'pico-safe-004', zone_id: 'room-4', device_name: 'Pico Safe 004', model: 'Raspberry Pi Pico 2W', status: 'online' }
];

const sensorLabels: Record<string, string> = {
  temperature: 'Temperature',
  humidity: 'Humidity',
  light: 'Light',
  motion: 'Motion'
};

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

function formatReading(reading: Reading | undefined, sensorId: string): string {
  if (!reading) return '--';
  if (sensorId === 'motion') return reading.value ? 'Motion' : 'No Motion';
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

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>('signin');
  const [authError, setAuthError] = useState('');
  const [authBusy, setAuthBusy] = useState(false);
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
      const session = await response.json();
      if (!cancelled) setIsAuthenticated(Boolean(session.authenticated));
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

  const timelineRows = timeline.length
    ? timeline
    : [{
      id: 'waiting',
      type: 'log',
      timestamp: new Date().toISOString(),
      title: 'waiting',
      message: 'Waiting for MQTT readings',
      tone: 'warning'
    }];
  const livenessDevices = liveness.devices.length ? liveness.devices : fallbackLiveness.devices;
  const livenessProcesses = liveness.processes.length ? liveness.processes : fallbackLiveness.processes;

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setAuthError('');

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
      setAuthError(authMode === 'signup' ? 'Could not create that account.' : 'Email or password did not match.');
      return;
    }

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
  }

  return (
    <main className="app-shell">
      <div className={isAuthenticated ? 'dashboard-shell' : 'dashboard-shell auth-locked'} aria-hidden={!isAuthenticated}>
        <header className="topbar">
          <div className="brand">
            <span className="brand-status" aria-hidden="true" />
            <div>
              <h1>Pico SafeRoom</h1>
              <span>Four-device Pico 2W safety monitor</span>
            </div>
            {isAuthenticated && (
              <button className="sign-out-button" type="button" onClick={handleLogout}>
                Sign out
              </button>
            )}
          </div>
          <div className={`safety ${safetyTone}`}>
            <span>Safety state</span>
            <strong>{health.safety_state === 'safe' ? 'Safe' : health.safety_state}</strong>
          </div>
          {Object.entries(health.processes).map(([name, state]) => (
            <div className="process" key={name}>
              <span>{name}</span>
              <strong><i className={statusTone(state)} />{state}</strong>
            </div>
          ))}
          <div className="timebox">
            <span>Uptime</span>
            <strong>{formatUptime(health.uptime_seconds)}</strong>
          </div>
          <div className="timebox">
            <span>Last update</span>
            <strong>{formatTime(health.last_update)}</strong>
          </div>
          <div className={`realtime ${realtimeState}`}>
            <span>Realtime</span>
            <strong><i />{realtimeState}</strong>
          </div>
        </header>

        <section className="workspace">
          <aside className="sidebar">
            <h2>Zones</h2>
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
            <h2>Devices</h2>
            <div className="device-card">
              <strong>{selectedDevice?.device_id}</strong>
              <span>{selectedDevice?.model}</span>
            </div>
          </aside>

          <section className="dashboard">
            <section className="panel">
              <div className="panel-title">
                <h2>Latest readings</h2>
                <span>{selectedDevice?.zone_id} / {selectedDevice?.device_id}</span>
              </div>
              <div className="reading-grid">
                {Object.keys(sensorLabels).map((sensorId, index) => {
                  const reading = selectedReadings[sensorId];
                  const quality = sensorQuality(reading);
                  const tone = qualityTone(quality);
                  return (
                    <article className={`reading-card ${tone}`} key={sensorId}>
                      <span className="sensor-name">{sensorLabels[sensorId]}</span>
                      <strong>{formatReading(reading, sensorId)}</strong>
                      <small className={`quality-badge ${tone}`}>{quality}</small>
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
                <h2>Blackbox timeline</h2>
                <span>{realtimeState === 'live' ? 'live websocket flow' : 'REST polling active'}</span>
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
              fallbackZone={selectedDevice?.zone_id ?? 'room-1'}
              formatTime={formatTime}
              statusTone={statusTone}
            />
            <section className="panel liveness-panel">
              <h2>Liveness</h2>
              <div className="liveness-group">
                <span>Devices</span>
                {livenessDevices.map((device) => (
                  <div className="liveness-row" key={device.device_id}>
                    <i className={statusTone(device.status)} />
                    <strong>{device.device_id}</strong>
                    <em>{device.status}</em>
                  </div>
                ))}
              </div>
              <div className="liveness-group">
                <span>Processes</span>
                {livenessProcesses.map((process) => (
                  <div className="liveness-row" key={process.process}>
                    <i className={statusTone(process.status)} />
                    <strong>{process.process}</strong>
                    <em>{process.status}</em>
                  </div>
                ))}
              </div>
            </section>
            <section className="panel logs">
              <h2>System log</h2>
              {(logs.length ? logs : [{ timestamp: new Date().toISOString(), level: 'info', message: 'Waiting for collector readings' }]).slice(0, 6).map((log, index) => (
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
          <span><strong>Last event:</strong> {logs[0]?.message ?? 'waiting for readings'}</span>
          <span><strong>Runtime:</strong> {formatUptime(health.uptime_seconds)}</span>
          <span><strong>Data flow:</strong> {realtimeState === 'live' ? 'websocket' : 'REST'}</span>
          <span><strong>Local time:</strong> {new Date().toLocaleTimeString()}</span>
        </footer>
      </div>

      {!isAuthenticated && (
        <section className="auth-backdrop" role="dialog" aria-modal="true" aria-labelledby="auth-title">
          <div className="auth-context">
            <span>Real-board mode</span>
            <strong>4 Pico 2W devices protected behind login</strong>
            <p>Local-first safety monitoring with MQTT, heartbeat, alerts, and blackbox timeline.</p>
          </div>

          <form className="auth-card" onSubmit={handleAuthSubmit}>
            <div className="auth-header">
              <span className="brand-status" aria-hidden="true" />
              <div>
                <h2 id="auth-title">Pico SafeRoom</h2>
                <p>Sign in to unlock the dashboard.</p>
              </div>
            </div>

            <div className="auth-tabs" aria-label="Authentication mode">
              <button
                type="button"
                className={authMode === 'signin' ? 'active' : ''}
                onClick={() => setAuthMode('signin')}
              >
                Sign in
              </button>
              <button
                type="button"
                className={authMode === 'signup' ? 'active' : ''}
                onClick={() => setAuthMode('signup')}
              >
                Create account
              </button>
            </div>

            <div className="social-auth">
              <button type="button" onClick={() => handleSocialAuth('google')}>
                <i className="google-dot" aria-hidden="true" />
                Continue with Google
              </button>
              <button type="button" onClick={() => handleSocialAuth('kakao')}>
                <i className="kakao-dot" aria-hidden="true" />
                Continue with Kakao
              </button>
            </div>

            <div className="auth-divider"><span>Email</span></div>

            <label>
              <span>Email</span>
              <input type="email" name="email" autoComplete="email" required />
            </label>
            <label>
              <span>Password</span>
              <input
                type="password"
                name="password"
                autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'}
                required
              />
            </label>
            {authError && <p className="auth-error">{authError}</p>}
            <button className="auth-submit" type="submit">
              {authBusy ? 'Checking...' : authMode === 'signup' ? 'Create account' : 'Sign in'}
            </button>
          </form>
        </section>
      )}
    </main>
  );
}
