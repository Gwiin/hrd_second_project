import { chromium } from '/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/index.mjs';

const url = 'http://127.0.0.1:8012/';
const screenshotPath = '/Users/chanpark/2n_project/.omo/evidence/language-toggle-korean-auth.png';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const mobileContext = await browser.newContext({ viewport: { width: 390, height: 800 } });
const mobilePage = await mobileContext.newPage();

await mobilePage.goto(url, { waitUntil: 'networkidle' });
await mobilePage.getByText('Sign in to unlock the dashboard.').waitFor({ timeout: 5000 });
await mobilePage.getByRole('button', { name: '한국어' }).click();
await mobilePage.getByText('대시보드를 열려면 로그인하세요.').waitFor({ timeout: 5000 });
await mobilePage.locator('input[name="email"]').fill('missing-mobile-user@example.com');
await mobilePage.locator('input[name="password"]').fill('password123');
await mobilePage.getByRole('button', { name: '로그인' }).last().click();
await mobilePage.getByText('이메일 또는 비밀번호가 일치하지 않습니다.').waitFor({ timeout: 5000 });
await mobilePage.getByRole('button', { name: 'English' }).click();
await mobilePage.getByText('Email or password did not match.').waitFor({ timeout: 5000 });
await mobileContext.close();

await page.goto(url, { waitUntil: 'networkidle' });
await page.getByText('Sign in to unlock the dashboard.').waitFor({ timeout: 5000 });
await page.locator('input[name="email"]').fill('missing-user@example.com');
await page.locator('input[name="password"]').fill('password123');
await page.getByRole('button', { name: 'Sign in' }).last().click();
await page.getByText('Email or password did not match.').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: '한국어' }).first().click();
await page.getByText('대시보드를 열려면 로그인하세요.').waitFor({ timeout: 5000 });
await page.getByText('로그인으로 보호되는 Pico 2W 장치 4대').waitFor({ timeout: 5000 });
await page.getByText('이메일 또는 비밀번호가 일치하지 않습니다.').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: 'English' }).first().click();
await page.getByText('Sign in to unlock the dashboard.').waitFor({ timeout: 5000 });
await page.getByText('Email or password did not match.').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: '한국어' }).first().click();
await page.getByRole('button', { name: '계정 만들기' }).click();
const email = `qa-user-${Date.now()}@example.com`;
const displayName = email.split('@', 1)[0];
await page.locator('input[name="email"]').fill(email);
await page.locator('input[name="password"]').fill('password123');
await page.getByRole('button', { name: '계정 만들기' }).last().click();
await page.getByText('로그인 사용자').waitFor({ timeout: 5000 });
await page.getByText(email).waitFor({ timeout: 5000 });
await page.getByText(displayName, { exact: true }).waitFor({ timeout: 5000 });
await page.getByText('인증 방식: email').waitFor({ timeout: 5000 });
await page.getByText('안전 상태').waitFor({ timeout: 5000 });
await page.getByText('최신 센서값').waitFor({ timeout: 5000 });
await page.getByText('시스템 로그').waitFor({ timeout: 5000 });
await page.getByText('활성 alert 없음').waitFor({ timeout: 5000 });
await page.locator('.incident-alert').getByText('정보', { exact: true }).waitFor({ timeout: 5000 });
await page.evaluate(async () => {
  const response = await fetch('/internal/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_id: `qa-temperature-alert-${Date.now()}`,
      site_id: 'safe-room-lab',
      zone_id: 'room-1',
      device_id: 'pico-safe-001',
      sensor_id: 'temperature',
      protocol: 'browser-qa',
      value: 61,
      unit: 'celsius',
      timestamp: new Date().toISOString(),
      quality: 'good',
      metadata: { source: 'language-toggle-qa' }
    })
  });
  if (!response.ok) throw new Error(`event ingest failed: ${response.status}`);
});
await page.locator('.safety').getByText('위험', { exact: true }).waitFor({ timeout: 5000 });
await page.getByText('온라인').first().waitFor({ timeout: 5000 });
await page.getByText('시뮬레이션').first().waitFor({ timeout: 5000 });
await page.getByText('정상').first().waitFor({ timeout: 5000 });
await page.getByText('누락').first().waitFor({ timeout: 5000 });
await page.getByText('열림').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: 'English' }).first().click();
await page.getByText('Safety state').waitFor({ timeout: 5000 });
await page.getByText('Latest readings').waitFor({ timeout: 5000 });
await page.getByText('System log').waitFor({ timeout: 5000 });
await page.locator('.safety').getByText('Critical', { exact: true }).waitFor({ timeout: 5000 });
await page.getByText('Online').first().waitFor({ timeout: 5000 });
await page.getByText('Simulated').first().waitFor({ timeout: 5000 });
await page.getByText('Good').first().waitFor({ timeout: 5000 });
await page.getByText('Missing').first().waitFor({ timeout: 5000 });
await page.getByRole('button', { name: '한국어' }).first().click();
await page.getByText('안전 상태').waitFor({ timeout: 5000 });
await page.locator('.safety').getByText('위험', { exact: true }).waitFor({ timeout: 5000 });
await page.locator('.incident-alert').getByText('위험', { exact: true }).waitFor({ timeout: 5000 });
await page.getByRole('button', { name: 'Incident 재생' }).click();
await page.getByRole('button', { name: '증거와 함께 확인' }).click();
await page.getByText('Incident 대응이 저장되었습니다.').waitFor({ timeout: 5000 });
await page.getByText('확인됨').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: 'English' }).first().click();
await page.getByText('Incident response saved.').waitFor({ timeout: 5000 });
await page.getByRole('button', { name: '한국어' }).first().click();
await page.getByText('Incident 대응이 저장되었습니다.').waitFor({ timeout: 5000 });
await page.screenshot({ path: screenshotPath, fullPage: true });
await browser.close();

console.log(JSON.stringify({
  ok: true,
  url,
  screenshotPath,
  verified: [
    'English auth subtitle appears by default',
    'Mobile unauthenticated auth card language toggle is visible and clickable',
    'Mobile failed-auth error rerenders across English/Korean toggles',
    'Failed auth error rerenders across English/Korean toggles',
    'Korean toggle changes auth subtitle and protected-device copy',
    'English toggle changes auth subtitle back',
    'Signup creates an authenticated session',
    'Logged-in user display shows name, email, and provider',
    'No-active-alert incident row translates info level in Korean mode',
    'Authenticated dashboard labels toggle English/Korean',
    'Finite status and quality labels translate in Korean mode',
    'Incident row status and level labels translate in Korean mode',
    'Incident saved status rerenders across English/Korean toggles',
    'Korean screenshot captured'
  ]
}, null, 2));
