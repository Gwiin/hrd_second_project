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

type ResponseReview = {
  readonly status: 'not_started' | 'partial' | 'complete';
  readonly completed_checklist: readonly string[];
  readonly missed_checklist: readonly ChecklistItem[];
  readonly unknown_checklist: readonly string[];
  readonly completion_ratio: number;
  readonly score_label: string;
  readonly next_best_action: string;
};

type AlertReplay = {
  readonly alert: IncidentAlert;
  readonly guidance: Guidance;
  readonly response: IncidentResponse | null;
  readonly response_review: ResponseReview;
  readonly related_events: readonly TimelineEntry[];
};

type IncidentReport = {
  readonly title: string;
  readonly response_review: ResponseReview;
  readonly operator_note: string;
  readonly operator_evidence: string;
  readonly missed_actions: readonly ChecklistItem[];
  readonly timeline: readonly TimelineEntry[];
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

function formatReviewStatusLabel(review: ResponseReview, copy: IncidentCopy): string {
  if (review.status === 'complete') return copy.responseComplete;
  if (review.status === 'partial') return copy.partialResponse;
  return copy.notStarted;
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
  const [report, setReport] = useState<IncidentReport | null>(null);
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
  const responseReview = report?.response_review ?? replay?.response_review ?? null;
  const reviewScorePercent = responseReview ? Math.round(responseReview.completion_ratio * 100) : 0;

  async function loadReplay(alertId: number) {
    setBusy(true);
    setMessageKey(null);
    const replayResponse = await fetch(`/api/alerts/${alertId}/replay`);
    setBusy(false);
    if (!replayResponse.ok) {
      setMessageKey('replayUnavailable');
      setReport(null);
      return;
    }
    const nextReplay: AlertReplay = await replayResponse.json();
    setReplay(nextReplay);
    setSelectedAlertId(alertId);
    const reportResponse = await fetch(`/api/alerts/${alertId}/report`);
    if (!reportResponse.ok) {
      setReport(null);
      return;
    }
    const reportBody: { readonly report: IncidentReport } = await reportResponse.json();
    setReport(reportBody.report);
  }

  async function handleResponseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedAlertId === null) return;
    const alertId = selectedAlertId;

    const form = new FormData(event.currentTarget);
    const checklist = form.getAll('response-checklist').map((value) => String(value));
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
        <span className="incident-section-label">{copy.drillTitle}</span>
        <strong>{guidance.summary}</strong>
        <p>{guidance.recommended_action}</p>
        <ul aria-label={copy.completedActions}>
          {guidance.checklist.map((item) => (
            <li key={item.id}>{item.label}</li>
          ))}
        </ul>
      </div>

      {responseReview && (
        <div className="incident-review-card">
          <div className="incident-review-main">
            <span
              className="incident-score-ring"
              style={{
                background: `radial-gradient(circle at center, rgba(255, 255, 255, 0.9) 0 52%, transparent 53%), conic-gradient(#19a974 0 ${reviewScorePercent}%, rgba(25, 169, 116, 0.16) ${reviewScorePercent}% 100%)`
              }}
            >
              {reviewScorePercent}%
            </span>
            <div className="incident-review-copy">
              <span className="incident-section-label">{copy.scoreLabel}</span>
              <strong>{formatReviewStatusLabel(responseReview, copy)}</strong>
              <small>{copy.nextBestAction}: {responseReview.next_best_action}</small>
            </div>
          </div>
          {responseReview.missed_checklist.length > 0 && (
            <ul aria-label={copy.missedActions}>
              {responseReview.missed_checklist.map((item) => (
                <li key={item.id}>{item.label}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <form className="incident-form" onSubmit={handleResponseSubmit}>
        <fieldset className="incident-checklist-card">
          <legend>{copy.completedActions}</legend>
          {guidance.checklist.map((item) => (
            <label className="incident-checklist-item" key={item.id}>
              <input
                type="checkbox"
                name="response-checklist"
                value={item.id}
                defaultChecked={response?.checklist.includes(item.id) ?? false}
              />
              <span>{item.label}</span>
            </label>
          ))}
        </fieldset>
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

      {report && (
        <div className="incident-report-card">
          <strong>{copy.reportTitle}</strong>
          <div>
            <span>{report.title}</span>
            <em>{copy.checklistComplete}: {report.response_review.completed_checklist.length}/{guidance.checklist.length}</em>
          </div>
          <small>{copy.timelineEvents}: {report.timeline.length}</small>
        </div>
      )}

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
