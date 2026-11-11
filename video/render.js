const { chromium } = require('playwright');
const path = require('path');
const dir = __dirname;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(dir, 'index.html'));
  const fps = 24, total = 100, n = total * fps;
  const only = process.argv[2] ? parseInt(process.argv[2]) : null;
  for (let i = 0; i < n; i++) {
    if (only !== null && i !== only) continue;
    const t = i / fps;
    await page.evaluate(t => window.render(t), t);
    await page.screenshot({ path: path.join(dir, 'frames', `f_${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 90 });
  }
  await browser.close();
  console.log('done');
})();
