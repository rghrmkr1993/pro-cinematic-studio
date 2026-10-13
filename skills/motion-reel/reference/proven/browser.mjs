// Launch Playwright chromium. Falls back to ANY installed chromium-NNNN/chrome-win64/chrome.exe when the
// revision Playwright expects (e.g. 1243) is not in %LOCALAPPDATA%\ms-playwright (e.g. only 1234 present).
import { chromium } from 'playwright';
import { readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
export async function launch() {
  try { return await chromium.launch(); } catch (e) {
    const root = join(process.env.LOCALAPPDATA || '', 'ms-playwright');
    const dirs = existsSync(root) ? readdirSync(root).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse() : [];
    for (const d of dirs) {
      const exe = join(root, d, 'chrome-win64', 'chrome.exe');
      if (existsSync(exe)) { console.error('[browser] default chromium missing, using ' + exe); return chromium.launch({ executablePath: exe }); }
    }
    throw e;
  }
}
