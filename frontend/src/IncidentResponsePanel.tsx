import { useEffect, useState, type FormEvent } from 'react';
import type { IncidentCopy, StatusLabelKey } from './language';

type IncidentAlert = {
  readonly alert_id: number | null;
  readonly level: string;
  readonly code: string;
  readonly message: string;
  readonly zone_id: string | null;
  readonly status: string;
};

type TimelineEntry = {
  readonly id: string;
  readonly type: string;
  readonly timestamp: string;
  readonly title: string;
  readonly message: string;
  readonly tone: string;
};

type ChecklistItem = {
  readonly id: string;
  readonly label: string;
};

type Guidance = {
  readonly summary: string;
  readonly recommended_action: string;
  readonly checklist: readonly ChecklistItem[];
};

type IncidentResponse = {
  readonly checklist: readonly string[];
  readonly note: string;
  readonly evidence: string;
};

type AlertReplay = {
  readonly alert: IncidentAlert;
  readonly guidance: Guidance;
  readonly response: IncidentResponse | null;
  readonly related_events: readonly TimelineEntry[];
};

type IncidentResponsePanelProps = {
  readonly alerts: readonly IncidentAlert[];
  readonly copy: IncidentCopy;
  readonly fallbackZone: string;
  readonly formatTime: (value: string | null) => string;
  readonly statusLabels: Record<StatusLabelKey, string>;
  readonly statusTone: (status: string) => string;
};

type IncidentMessageKey = 'replayUnavailable' | 'saveFailed' | 'saved';

function formatIncidentStatusLabel(status: string, labels: Record<StatusLabelKey, string>): string {
  return labels[status as StatusLabelKey] ?? status;
}

export function IncidentResponsePanel({
  alerts,
  copy,
  fallbackZone,
  formatTime,
  statusLabels,
  statusTone
}: IncidentResponsePanelProps) {
  const replayableAlerts = alerts.filter((alert) => alert.alert_id !== null);
  const [selectedAlertId, setSelectedAlertId] = useState<number | null>(null);
  const [replay, setReplay] = useState<AlertReplay | null>(null);
  const [busy, setBusy] = useState(false);
  const [messageKey, setMessageKey] = useState<IncidentMessageKey | null>(null);

  useEffect(() => {
    if (selectedAlertId !== null) return;
    setSelectedAlertId(replayableAlerts[0]?.alert_id ?? null);
  }, [replayableAlerts, selectedAlertId]);

  const selectedAlert = alerts.find((alert) => alert.alert_id === selectedAlertId) ?? alerts[0] ?? null;
  const guidance = replay?.guidance ?? {
    summary: copy.fallbackSummary,
    recommended_action: copy.fallbackAction,
    checklist: []
  };
  const response = replay?.response ?? null;

  async function loadReplay(alertId: number) {
    setBusy(true);
    setMessageKey(null);
    const replayResponse = await fetch(`/api/alerts/${alertId}/replay`);
    setBusy(false);
    if (!replayResponse.ok) {
      setMessageKey('replayUnavailable');
      return;
    }
    const nextReplay: AlertReplay = await replayResponse.json();
    setReplay(nextReplay);
    setSelectedAlertId(alertId);
  }

  async function handleResponseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedAlertId === null) return;
    const alertId = selectedAlertId;

    const form = new FormData(event.currentTarget);
    const checklist = guidance.checklist.map((item) => item.id);
    const payload = {
      checklist,
      note: String(form.get('response-note') ?? ''),
      evidence: String(form.get('response-evidence') ?? '')
    };

    setBusy(true);
    const responseResult = await fetch(`/api/alerts/${alertId}/ack`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    setBusy(false);

    if (!responseResult.ok) {
      setMessageKey('saveFailed');
      return;
    }

    await loadReplay(alertId);
    setMessageKey('saved');
  }

  return (
    <section className="panel alerts incident-response-panel">
      <div className="incident-header">
        <div>
          <h2>{copy.title}</h2>
          <span>{selectedAlert?.zone_id ?? fallbackZone}</span>
        </div>
        <button
          type="button"
          disabled={selectedAlertId === null || busy}
          onClick={() => {
            if (selectedAlertId !== null) void loadReplay(selectedAlertId);
          }}
        >
          {copy.replay}
        </button>
      </div>

      {(alerts.length ? alerts : [{ alert_id: null, level: 'info', code: 'none', message: copy.noActiveAlert, zone_id: fallbackZone, status: 'open' }]).slice(0, 5).map((alert) => {
        const alertId = alert.alert_id;
        const replayable = alertId !== null;
        return (
          <button
            className={alertId === selectedAlertId ? 'incident-alert active' : 'incident-alert'}
            key={`${alert.message}-${alert.zone_id ?? 'site'}`}
            type="button"
            disabled={!replayable}
            onClick={() => {
              if (alertId !== null) {
                setSelectedAlertId(alertId);
                void loadReplay(alertId);
              }
            }}
          >
            <i className={statusTone(alert.level)} />
            <span>
              <strong>{alert.message}</strong>
              <small>{replayable ? formatIncidentStatusLabel(alert.status, statusLabels) : copy.notReplayable}</small>
            </span>
            <em className={statusTone(alert.level)}>{formatIncidentStatusLabel(alert.level, statusLabels)}</em>
          </button>
        );
      })}

      <div className="incident-guidance">
        <strong>{guidance.summary}</strong>
        <p>{guidance.recommended_action}</p>
        <ul>
          {guidance.checklist.map((item) => (
            <li key={item.id}>{item.label}</li>
          ))}
        </ul>
      </div>

      <form className="incident-form" onSubmit={handleResponseSubmit}>
        <label>
          <span>{copy.responseNote}</span>
          <textarea name="response-note" maxLength={500} defaultValue={response?.note ?? ''} />
        </label>
        <label>
          <span>{copy.evidence}</span>
          <textarea name="response-evidence" maxLength={500} defaultValue={response?.evidence ?? ''} />
        </label>
        <button type="submit" disabled={selectedAlertId === null || busy}>
          {busy ? copy.saving : copy.acknowledge}
        </button>
        {messageKey && <small>{copy[messageKey]}</small>}
      </form>

      {replay && (
        <div className="incident-replay">
          <strong>{copy.replayTimeline}</strong>
          {replay.related_events.slice(0, 4).map((entry) => (
            <div className="incident-event" key={entry.id}>
              <time>{formatTime(entry.timestamp)}</time>
              <span>{entry.title}</span>
              <em>{entry.type.replace('_', ' ')}</em>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
