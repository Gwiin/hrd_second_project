import { chromium } from "/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/index.mjs";
import { writeFile } from "node:fs/promises";

const base = "http://127.0.0.1:8767";
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
const request = context.request;

const eventResponse = await request.post(`${base}/internal/events`, {
  data: {
    event_id: "incident-drill-browser-gas-20260605e",
    site_id: "safe-room-lab",
    zone_id: "room-1",
    device_id: "pico-safe-001",
    sensor_id: "gas",
    protocol: "mock",
    value: 601,
    unit: "ppm",
    timestamp: "2026-06-05T13:10:00+09:00",
    quality: "good",
    metadata: { qa: "browser-incident-drill" }
  }
});
const signupResponse = await request.post(`${base}/api/auth/signup`, {
  data: { email: "incident-drill-qa5@example.com", password: "strong-pass-12345" }
});

const page = await context.newPage();
await page.goto(base, { waitUntil: "networkidle" });
await page.getByRole("button", { name: /Replay incident/i }).click();
await page.getByRole("checkbox", { name: /Move people away from the room/i }).check();
await page.getByLabel(/Response note/i).fill("Browser QA started evacuation only.");
await page.getByLabel(/Evidence/i).fill("Browser QA evidence captured.");
await page.getByRole("button", { name: /Acknowledge with evidence/i }).click();
await page.getByText(/Partial response/i).waitFor({ timeout: 10000 });
await page.locator(".incident-review small", { hasText: /Open ventilation or windows/i }).waitFor({ timeout: 10000 });
await page.getByText("Incident command report", { exact: true }).waitFor({ timeout: 10000 });
await page.screenshot({ path: ".omo/evidence/incident-drill-browser.png", fullPage: true });

const receipt = {
  eventStatus: eventResponse.status(),
  signupStatus: signupResponse.status(),
  title: await page.title(),
  visibleText: (await page.locator(".incident-response-panel").innerText()).split("\n").filter(Boolean).slice(0, 40),
  checkedCount: await page.locator('input[name="response-checklist"]:checked').count(),
  uncheckedCount: await page.locator('input[name="response-checklist"]:not(:checked)').count()
};
await writeFile(".omo/evidence/incident-drill-browser-actions.txt", JSON.stringify(receipt, null, 2));
await browser.close();
console.log(JSON.stringify(receipt, null, 2));
