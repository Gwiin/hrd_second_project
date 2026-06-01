import { useEffect, useMemo, useState } from 'react';

type Device = {
  device_id: string;
  zone_id: string;
  device_name: string;
  model: string;
  status: string;
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

type LatestReadings = Record<string, Record<string, Reading>>;

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
  motion: 'Motion',
  gas: 'Gas'
};

const fallbackHealth: Health = {
  app: 'Pico SafeRoom',
  status: 'starting',
  safety_state: 'safe',
  uptime_seconds: 0,
  last_update: null,
  processes: {
    backend: 'connecting',
    collector: 'simulated',
    worker: 'simulated'
  }
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

function sparkline(seed: number): string {
  return Array.from({ length: 20 }, (_, index) => {
    const x = 5 + index * 8;
    const y = 32 - (Math.sin(index / 2 + seed) * 7 + Math.cos(index / 3 + seed) * 4);
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ');
}

function statusTone(status: string): string {
  if (status === 'critical') return 'critical';
  if (status === 'warning') return 'warning';
  return 'safe';
}

export default function App() {
  const [devices, setDevices] = useState<Device[]>(fallbackDevices);
  const [selectedDeviceId, setSelectedDeviceId] = useState('pico-safe-001');
  const [health, setHealth] = useState<Health>(fallbackHealth);
  const [readings, setReadings] = useState<LatestReadings>({});
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      const [healthResponse, devicesResponse, readingsResponse, logsResponse] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/devices'),
        fetch('/api/readings/latest'),
        fetch('/api/logs')
      ]);
      if (cancelled) return;
      setHealth(await healthResponse.json());
      setDevices((await devicesResponse.json()).devices);
      setReadings((await readingsResponse.json()).readings);
      setLogs((await logsResponse.json()).logs);
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

  const selectedDevice = devices.find((device) => device.device_id === selectedDeviceId) ?? devices[0];
  const selectedReadings = readings[selectedDevice?.device_id] ?? {};
  const safetyTone = statusTone(health.safety_state);

  const recentAlerts = useMemo(
    () => [
      { level: 'Info', message: 'All clear', room: selectedDevice?.zone_id ?? 'room-1', tone: 'safe' },
      { level: health.safety_state === 'safe' ? 'Info' : 'Warning', message: health.safety_state === 'safe' ? 'No active alert' : 'Safety threshold warning', room: selectedDevice?.zone_id ?? 'room-1', tone: safetyTone },
      { level: 'Info', message: 'Four Pico 2W devices registered', room: 'site', tone: 'safe' }
    ],
    [health.safety_state, safetyTone, selectedDevice?.zone_id]
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="shield">P</div>
          <div>
            <h1>Pico SafeRoom</h1>
            <span>Four-device Pico 2W safety monitor</span>
          </div>
        </div>
        <div className={`safety ${safetyTone}`}>
          <span>Safety state</span>
          <strong>{health.safety_state === 'safe' ? 'Safe' : health.safety_state}</strong>
        </div>
        {Object.entries(health.processes).map(([name, state]) => (
          <div className="process" key={name}>
            <span>{name}</span>
            <strong><i />{state}</strong>
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
                <i />
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
              {Object.keys(sensorLabels).map((sensorId, index) => (
                <article className="reading-card" key={sensorId}>
                  <span className="sensor-name">{sensorLabels[sensorId]}</span>
                  <strong>{formatReading(selectedReadings[sensorId], sensorId)}</strong>
                  <small>{selectedReadings[sensorId]?.quality ?? 'waiting'}</small>
                  <svg viewBox="0 0 170 44" aria-hidden="true">
                    <path d={sparkline(index + selectedDeviceId.length)} />
                  </svg>
                </article>
              ))}
            </div>
          </section>

          <section className="panel timeline-panel">
            <div className="panel-title">
              <h2>Readings timeline</h2>
              <span>mock Level 1 flow</span>
            </div>
            <div className="timeline">
              <div className="axis-labels">
                <span>Temperature</span>
                <span>Humidity</span>
                <span>Light</span>
                <span>Gas</span>
              </div>
              <svg viewBox="0 0 900 250" aria-label="Sensor trend lines">
                <g className="grid-lines">
                  {[0, 1, 2, 3, 4].map((line) => (
                    <line key={line} x1="40" x2="870" y1={35 + line * 42} y2={35 + line * 42} />
                  ))}
                </g>
                <path className="trend red" d="M40 95 C170 80 250 130 370 105 S560 70 690 100 S810 120 870 90" />
                <path className="trend blue" d="M40 135 C190 145 280 120 390 132 S560 148 700 126 S820 112 870 116" />
                <path className="trend yellow" d="M40 185 C210 190 290 178 360 150 S470 45 580 105 S700 180 870 168" />
                <path className="trend green" d="M40 165 C190 160 310 168 420 158 S610 145 730 154 S820 150 870 148" />
              </svg>
            </div>
          </section>
        </section>

        <aside className="right-rail">
          <section className="panel alerts">
            <h2>Recent alerts</h2>
            {recentAlerts.map((alert) => (
              <div className="alert-row" key={`${alert.message}-${alert.room}`}>
                <i className={alert.tone} />
                <div>
                  <strong>{alert.message}</strong>
                  <span>{alert.room}</span>
                </div>
                <em>{alert.level}</em>
              </div>
            ))}
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
        <span><strong>Data rate:</strong> simulated</span>
        <span><strong>Local time:</strong> {new Date().toLocaleTimeString()}</span>
      </footer>
    </main>
  );
}
