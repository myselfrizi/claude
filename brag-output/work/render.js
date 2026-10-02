const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
(async () => {
  const mode = process.argv[2]; // "stills" or "frames"
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' + '-1194/chrome-linux/chrome' }).catch(async () => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'scene.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const stage = await page.$('#stage');
  if (mode === 'stills') {
    const ts = process.argv.slice(3).map(Number);
    for (const t of ts) {
      await page.evaluate(t => window.render(t), t);
      await stage.screenshot({ path: path.join(__dirname, 'stills', `t${t.toFixed(2)}.png`) });
    }
  } else {
    const fps = 30, dur = 13, n = fps * dur;
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      await stage.screenshot({ path: path.join(__dirname, 'frames', `f${String(i).padStart(4, '0')}.png`) });
    }
  }
  await browser.close();
})();
