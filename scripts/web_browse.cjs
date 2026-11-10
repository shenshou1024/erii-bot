// ============================================================
// ⚠️ 网页浏览截图脚本自 v0.2.3 起默认禁用（源码保留待修复）
// 原因：与 QQagent 多客户端 WebSocket 冲突，截图偶发崩溃占用资源
// ============================================================
const fs = require('fs');
const path = require('path');
const puppeteer = require('/opt/QQagent/node_modules/puppeteer-extra');
const StealthPlugin = require('/opt/QQagent/node_modules/puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

// 持久化浏览器数据目录：复用 cookie / 缓存，模拟老用户，降低风控验证码概率
const USER_DATA_DIR = '/tmp/edge-erii-profile';

// 随机延迟（毫秒）
const sleep = (min, max) => new Promise(r => setTimeout(r, min + Math.random() * (max - min)));

// 清理上次异常退出残留的 profile 锁文件
function cleanProfileLock() {
  ['SingletonLock', 'SingletonCookie', 'SingletonSocket'].forEach(f => {
    const p = path.join(USER_DATA_DIR, f);
    try { if (fs.existsSync(p)) fs.unlinkSync(p); } catch (e) {}
  });
}

// 注入反自动化检测脚本
async function applyAntiDetection(page) {
  await page.evaluateOnNewDocument(() => {
    // 隐藏 webdriver 标记
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    // 伪造语言
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
    // 伪造插件列表
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    // 伪造 chrome 运行时
    window.chrome = { runtime: {} };
    // 修正权限查询
    const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
    if (originalQuery) {
      window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
          ? Promise.resolve({ state: 'prompt' })
          : originalQuery(parameters);
    }
    // 伪装 WebGL 渲染厂商
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (parameter) {
      if (parameter === 37445) return 'Intel Inc.';
      if (parameter === 37446) return 'Intel Iris OpenGL Engine';
      return getParameter.call(this, parameter);
    };
  });
}

// 检测当前页面是否出现验证码 / 人机验证
async function detectCaptcha(page) {
  try {
    return await page.evaluate(() => {
      const text = document.body ? (document.body.innerText || '') : '';
      const keywords = ['安全验证', '滑动验证', '点选验证', '拖动滑块', '请完成验证', '人机验证', '验证码', '安全校验'];
      if (keywords.some(k => text.includes(k))) return true;
      const iframes = document.querySelectorAll('iframe');
      for (const f of iframes) {
        const src = (f.src || '').toLowerCase();
        if (src.includes('captcha') || src.includes('verify') || src.includes('geetest') ||
            src.includes('aliyun') || src.includes('tc-captcha') || src.includes('ncaptcha')) return true;
      }
      // 常见验证码容器
      if (document.querySelector('.captcha, .nc-container, #captcha, [class*="captcha"], [class*="verify-code"]')) return true;
      return false;
    });
  } catch (e) {
    return false;
  }
}

// 模拟真人分段滚动浏览
async function humanScroll(page, times) {
  const count = times || 2;
  for (let i = 0; i < count; i++) {
    await sleep(1200, 2800);
    const dist = 150 + Math.floor(Math.random() * 220);
    try { await page.evaluate((d) => window.scrollBy(0, d), dist); } catch (e) {}
  }
}

async function browseAndScreenshot(url, outputPath) {
  console.log('启动 Edge 浏览...');
  cleanProfileLock();

  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/microsoft-edge',
    userDataDir: USER_DATA_DIR,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-blink-features=AutomationControlled',
      '--window-size=1280,800'
    ]
  });

  const page = await browser.newPage();
  await applyAntiDetection(page);

  const isBilibili = url.includes('bilibili.com');
  const isXiaoheihe = url.includes('xiaoheihe.cn');

  if (isBilibili) {
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1');
    await page.setViewport({ width: 375, height: 667 });
    if (url.includes('www.bilibili.com')) {
      url = url.replace('www.bilibili.com', 'm.bilibili.com');
    }
  } else {
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0');
    await page.setViewport({ width: 1280, height: 800 });
  }
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8' });

  let captchaDetected = false;
  let clicked = false;
  let pageTitle = '';

  try {
    // ===== 小黑盒：先逛主页养一养，再进社区，规避点选验证码 =====
    if (isXiaoheihe) {
      console.log('先访问小黑盒主页模拟浏览...');
      try {
        await page.goto('https://xiaoheihe.cn', { waitUntil: 'domcontentloaded', timeout: 30000 });
        await sleep(2500, 4000);
        await humanScroll(page, 2 + Math.floor(Math.random() * 2));

        if (await detectCaptcha(page)) {
          console.log('主页出现验证，刷新一次再观察...');
          await page.reload({ waitUntil: 'domcontentloaded', timeout: 30000 });
          await sleep(3000, 4000);
          captchaDetected = await detectCaptcha(page);
        }
      } catch (e) {
        console.log('主页访问异常: ' + e.message);
      }
    }

    // ===== 打开目标页面 =====
    console.log('打开页面: ' + url);
    try {
      await page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout: 30000,
        referer: isXiaoheihe ? 'https://xiaoheihe.cn' : undefined
      });
    } catch (e) {
      console.log('打开页面失败: ' + e.message);
    }

    await sleep(3000, 5000);
    await humanScroll(page, 2);

    // ===== 验证码检测：小黑盒优先，检测到就不点击内容，避免截到验证页 =====
    if (isXiaoheihe) {
      captchaDetected = captchaDetected || await detectCaptcha(page);
      if (captchaDetected) {
        console.log('⚠️ 检测到小黑盒安全验证，放弃点帖子，回退主页截图');
      }
    }

    // ===== 点击内容卡片（有验证码时跳过）=====
    if (!captchaDetected) {
      try {
        let selector = null;
        if (isBilibili) {
          selector = 'a[href*="/video/"]';
        } else if (isXiaoheihe) {
          selector = '.hb-cpt__bbs-list-content, .bbs-item, a[href*="/bbs/"]';
        } else if (url.includes('4399.com')) {
          selector = 'a[href*="/flash/"]';
        }

        if (selector) {
          const links = await page.$$(selector);
          if (links.length > 0) {
            console.log('发现 ' + links.length + ' 个内容卡片，随机点一个...');
            const randomIndex = Math.floor(Math.random() * links.length);
            const randomLink = links[randomIndex];

            let href = await randomLink.evaluate(el => el.href);
            console.log('原始链接: ' + href);

            if (isBilibili && href.includes('www.bilibili.com')) {
              href = href.replace('www.bilibili.com', 'm.bilibili.com');
              console.log('改成手机版: ' + href);
            }

            try {
              await page.goto(href, {
                waitUntil: 'domcontentloaded',
                timeout: 20000,
                referer: url
              });
              clicked = true;
              await sleep(3000, 5000);

              // 跳转后再次检测验证码
              if (await detectCaptcha(page)) {
                console.log('点进去后出现验证，回退到列表页');
                captchaDetected = true;
                clicked = false;
                await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});
                await sleep(2000, 3000);
              } else {
                console.log('内容页面加载完成');
              }

              // B站自动播放
              if (isBilibili && !captchaDetected) {
                try {
                  const playBtn = await page.evaluateHandle(() => {
                    const buttons = Array.from(document.querySelectorAll('button, a, div'));
                    return buttons.find(b => b.textContent && b.textContent.includes('立即播放'));
                  });
                  if (playBtn) {
                    console.log('点击立即播放按钮...');
                    await playBtn.click();
                    await sleep(2000, 3000);
                    console.log('开始播放了');
                  }
                } catch (e) {
                  console.log('点击播放失败: ' + e.message);
                }
              }
            } catch (e) {
              console.log('跳转失败，就截首页吧: ' + e.message);
            }
          }
        }
      } catch (e) {
        console.log('点击失败，就在首页看看: ' + e.message);
      }
    }

    await sleep(1500, 2500);

    try {
      pageTitle = await page.title();
      console.log('页面标题: ' + pageTitle);
    } catch (e) {
      console.log('提取标题失败');
    }

    if (captchaDetected) {
      pageTitle = (pageTitle ? pageTitle + ' ' : '') + '（触发安全验证，当前为列表/主页画面）';
    }

    try {
      await page.evaluate(() => window.scrollBy(0, 200));
    } catch (e) {
      console.log('滚动失败: ' + e.message);
    }
    await sleep(1000, 1800);

    try {
      await page.screenshot({ path: outputPath, fullPage: false });
      console.log('截图已保存: ' + outputPath);
      if (clicked) console.log('（这是点进去后的内容页面）');
    } catch (e) {
      console.log('截图失败: ' + e.message);
    }
  } finally {
    try { await browser.close(); } catch (e) {}
  }

  console.log('---内容开始---');
  console.log(pageTitle);
  console.log('---内容结束---');
}

const url = process.argv[2];
const output = process.argv[3] || '/tmp/screenshot.png';

if (!url) {
  console.log('用法: node web_browse.cjs <url> [output]');
  process.exit(1);
}

browseAndScreenshot(url, output).catch(err => {
  console.error('失败:', err.message);
  process.exit(1);
});
