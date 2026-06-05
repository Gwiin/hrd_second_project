export type Language = 'en' | 'ko';
export type SensorId = 'temperature' | 'humidity' | 'light' | 'motion' | 'gas';
export type StatusLabelKey = 'safe' | 'warning' | 'critical' | 'info' | 'online' | 'offline' | 'connecting' | 'simulated' | 'degraded' | 'open' | 'acknowledged' | 'reconnecting' | 'live';
export type QualityLabelKey = 'good' | 'uncertain' | 'bad' | 'stale' | 'missing';

export type IncidentCopy = {
  readonly fallbackSummary: string;
  readonly fallbackAction: string;
  readonly replayUnavailable: string;
  readonly saveFailed: string;
  readonly saved: string;
  readonly title: string;
  readonly replay: string;
  readonly noActiveAlert: string;
  readonly notReplayable: string;
  readonly responseNote: string;
  readonly evidence: string;
  readonly acknowledge: string;
  readonly saving: string;
  readonly replayTimeline: string;
  readonly reportTitle: string;
  readonly nextAction: string;
  readonly checklistComplete: string;
  readonly timelineEvents: string;
};

export const languageOptions: readonly { readonly id: Language; readonly label: string }[] = [
  { id: 'en', label: 'English' },
  { id: 'ko', label: '한국어' }
];

export const sensorIds: readonly SensorId[] = ['temperature', 'humidity', 'light', 'motion', 'gas'];

export const copyByLanguage = {
  en: {
    app: {
      language: 'Language',
      subtitle: 'Four-device Pico 2W safety monitor',
      safetyState: 'Safety state',
      safe: 'Safe',
      uptime: 'Uptime',
      lastUpdate: 'Last update',
      realtime: 'Realtime',
      zones: 'Zones',
      devices: 'Devices',
      latestReadings: 'Latest readings',
      blackboxTimeline: 'Blackbox timeline',
      liveFlow: 'live websocket flow',
      restPolling: 'REST polling active',
      liveness: 'Liveness',
      processes: 'Processes',
      systemLog: 'System log',
      lastEvent: 'Last event',
      runtime: 'Runtime',
      dataFlow: 'Data flow',
      localTime: 'Local time',
      waitingForMqtt: 'Waiting for MQTT readings',
      waitingForCollector: 'Waiting for collector readings',
      waitingForReadings: 'waiting for readings',
      signedInAs: 'Signed in as',
      authProvider: 'Provider',
      signOut: 'Sign out',
      views: 'Views',
      dashboard: 'Dashboard',
      motion: 'Motion',
      noMotion: 'No Motion',
      llmPreviewTitle: 'LLM assistant preview',
      llmPreviewBadge: 'Prepared from statistics',
      llmPreviewBody: 'Statistics-based assistance will appear here after the LLM connection is added.',
      llmPreviewPrompt: 'Ask about safety trends, stale sensors, or room conditions',
      llmPreviewSend: 'Ready soon'
    },
    sensors: {
      temperature: 'Temperature',
      humidity: 'Humidity',
      light: 'Light',
      motion: 'Motion',
      gas: 'Gas'
    },
    statusLabels: {
      safe: 'Safe',
      warning: 'Warning',
      critical: 'Critical',
      info: 'Info',
      online: 'Online',
      offline: 'Offline',
      connecting: 'Connecting',
      simulated: 'Simulated',
      degraded: 'Degraded',
      open: 'Open',
      acknowledged: 'Acknowledged',
      reconnecting: 'Reconnecting',
      live: 'Live'
    },
    qualityLabels: {
      good: 'Good',
      uncertain: 'Uncertain',
      bad: 'Bad',
      stale: 'Stale',
      missing: 'Missing'
    },
    auth: {
      realBoardMode: 'Real-board mode',
      protectedDevices: '4 Pico 2W devices protected behind login',
      description: 'Local-first safety monitoring with MQTT, heartbeat, alerts, and blackbox timeline.',
      subtitle: 'Sign in to unlock the dashboard.',
      modeLabel: 'Authentication mode',
      signIn: 'Sign in',
      createAccount: 'Create account',
      continueGoogle: 'Continue with Google',
      continueKakao: 'Continue with Kakao',
      email: 'Email',
      password: 'Password',
      checking: 'Checking...',
      signupError: 'Could not create that account.',
      signinError: 'Email or password did not match.'
    },
    incident: {
      fallbackSummary: 'No incident selected',
      fallbackAction: 'Select a replayable alert to view response guidance.',
      replayUnavailable: 'Incident replay unavailable.',
      saveFailed: 'Could not save response evidence.',
      saved: 'Incident response saved.',
      title: 'Incident response',
      replay: 'Replay incident',
      noActiveAlert: 'No active alert',
      notReplayable: 'not replayable',
      responseNote: 'Response note',
      evidence: 'Evidence',
      acknowledge: 'Acknowledge with evidence',
      saving: 'Saving...',
      replayTimeline: 'Replay timeline',
      reportTitle: 'Incident report',
      nextAction: 'Next action',
      checklistComplete: 'Checklist complete',
      timelineEvents: 'Timeline events'
    } satisfies IncidentCopy,
    stats: {
      title: 'Statistics',
      description: 'Operational statistics from the data already visible on the dashboard.',
      safetyState: 'Safety state',
      devicesOnline: 'Devices online',
      totalReadings: 'Total readings',
      openAlerts: 'Open alerts',
      staleSensors: 'Stale sensors',
      sensorBreakdown: 'Sensor breakdown',
      deviceBreakdown: 'Device breakdown',
      alertBreakdown: 'Alert breakdown',
      totalAlerts: 'Total alerts',
      offlineDevices: 'Offline devices',
      latestSensors: 'Latest sensors',
      count: 'Count',
      latest: 'Latest',
      average: 'Average',
      motionTrue: 'Motion true',
      emptySensors: 'No sensor readings yet.',
      loading: 'Loading statistics',
      loadingBody: 'Waiting for the backend statistics summary.',
      errorTitle: 'Statistics unavailable',
      errorBody: 'The dashboard is still usable while statistics reconnect.',
      llmContext: 'Future LLM-ready summary',
      llmContextPreview: 'LLM context preview',
      environmentByRoom: 'Environment by room',
      environmentByRoomBody: 'Latest environment values from each room.',
      recentEnvironmentTrend: 'Recent environment trend',
      recentEnvironmentTrendBody: 'Recent reading events from the blackbox timeline.',
      noRoomData: 'No latest reading',
      noRecentTrend: 'Not enough recent sensor history yet.'
    }
  },
  ko: {
    app: {
      language: '언어',
      subtitle: 'Pico 2W 4대 안전 관제',
      safetyState: '안전 상태',
      safe: '안전',
      uptime: '실행 시간',
      lastUpdate: '마지막 갱신',
      realtime: '실시간',
      zones: '구역',
      devices: '장치',
      latestReadings: '최신 센서값',
      blackboxTimeline: '블랙박스 타임라인',
      liveFlow: 'WebSocket 실시간 흐름',
      restPolling: 'REST 폴링 중',
      liveness: '상태 감시',
      processes: '프로세스',
      systemLog: '시스템 로그',
      lastEvent: '마지막 이벤트',
      runtime: '런타임',
      dataFlow: '데이터 흐름',
      localTime: '로컬 시간',
      waitingForMqtt: 'MQTT 센서값 대기 중',
      waitingForCollector: '수집기 센서값 대기 중',
      waitingForReadings: '센서값 대기 중',
      signedInAs: '로그인 사용자',
      authProvider: '인증 방식',
      signOut: '로그아웃',
      views: '보기',
      dashboard: '대시보드',
      motion: '움직임',
      noMotion: '움직임 없음',
      llmPreviewTitle: '통계 기반 LLM 상담 준비 중',
      llmPreviewBadge: '통계 컨텍스트 준비됨',
      llmPreviewBody: 'LLM 연결이 추가되면 이 영역에서 안전 추이와 방별 상태를 질문할 수 있습니다.',
      llmPreviewPrompt: '안전 추이, 오래된 센서, 방 상태를 질문할 수 있습니다',
      llmPreviewSend: '준비 중'
    },
    sensors: {
      temperature: '온도',
      humidity: '습도',
      light: '조도',
      motion: '움직임',
      gas: '가스'
    },
    statusLabels: {
      safe: '안전',
      warning: '주의',
      critical: '위험',
      info: '정보',
      online: '온라인',
      offline: '오프라인',
      connecting: '연결 중',
      simulated: '시뮬레이션',
      degraded: '저하',
      open: '열림',
      acknowledged: '확인됨',
      reconnecting: '재연결 중',
      live: '실시간'
    },
    qualityLabels: {
      good: '정상',
      uncertain: '불확실',
      bad: '불량',
      stale: '오래됨',
      missing: '누락'
    },
    auth: {
      realBoardMode: '실제 보드 모드',
      protectedDevices: '로그인으로 보호되는 Pico 2W 장치 4대',
      description: 'MQTT, heartbeat, alert, 블랙박스 타임라인을 포함한 로컬 우선 안전 관제입니다.',
      subtitle: '대시보드를 열려면 로그인하세요.',
      modeLabel: '인증 모드',
      signIn: '로그인',
      createAccount: '계정 만들기',
      continueGoogle: 'Google로 계속',
      continueKakao: 'Kakao로 계속',
      email: '이메일',
      password: '비밀번호',
      checking: '확인 중...',
      signupError: '계정을 만들 수 없습니다.',
      signinError: '이메일 또는 비밀번호가 일치하지 않습니다.'
    },
    incident: {
      fallbackSummary: '선택된 incident가 없습니다',
      fallbackAction: '재생 가능한 alert를 선택하면 대응 가이드를 볼 수 있습니다.',
      replayUnavailable: 'Incident 재생을 사용할 수 없습니다.',
      saveFailed: '대응 증거를 저장할 수 없습니다.',
      saved: 'Incident 대응이 저장되었습니다.',
      title: 'Incident 대응',
      replay: 'Incident 재생',
      noActiveAlert: '활성 alert 없음',
      notReplayable: '재생 불가',
      responseNote: '대응 메모',
      evidence: '증거',
      acknowledge: '증거와 함께 확인',
      saving: '저장 중...',
      replayTimeline: '재생 타임라인',
      reportTitle: 'Incident report',
      nextAction: '다음 조치',
      checklistComplete: '체크리스트 완료',
      timelineEvents: '타임라인 이벤트'
    } satisfies IncidentCopy,
    stats: {
      title: '통계',
      description: '대시보드에 보이는 데이터를 기준으로 만든 운영 통계입니다.',
      safetyState: '안전 상태',
      devicesOnline: '온라인 장치',
      totalReadings: '총 센서값',
      openAlerts: '열린 alert',
      staleSensors: '오래된 센서',
      sensorBreakdown: '센서별 통계',
      deviceBreakdown: '장치별 통계',
      alertBreakdown: 'Alert 통계',
      totalAlerts: '전체 alert',
      offlineDevices: '오프라인 장치',
      latestSensors: '최근 센서 수',
      count: '개수',
      latest: '최근값',
      average: '평균',
      motionTrue: '움직임 감지',
      emptySensors: '아직 센서값이 없습니다.',
      loading: '통계 불러오는 중',
      loadingBody: 'Backend 통계 요약을 기다리는 중입니다.',
      errorTitle: '통계를 사용할 수 없습니다',
      errorBody: '통계가 재연결되는 동안 대시보드는 계속 사용할 수 있습니다.',
      llmContext: '향후 LLM용 요약',
      llmContextPreview: 'LLM 분석 컨텍스트',
      environmentByRoom: '방별 환경',
      environmentByRoomBody: '각 방에서 마지막으로 수집된 환경 값입니다.',
      recentEnvironmentTrend: '최근 환경 추이',
      recentEnvironmentTrendBody: '블랙박스 타임라인의 최근 센서 이벤트입니다.',
      noRoomData: '최근 센서값 없음',
      noRecentTrend: '최근 센서 이력이 아직 부족합니다.'
    }
  }
} as const;
