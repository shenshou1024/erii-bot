// ============================================================
// ⚠️ 网页浏览截图脚本自 v0.2.3 起默认禁用（源码保留待修复）
// 原因：与 QQagent 多客户端 WebSocket 冲突，截图偶发崩溃占用资源
// ============================================================
const puppeteer = require('/opt/QQagent/node_modules/puppeteer-extra');
const StealthPlugin = require('/opt/QQagent/node_modules/puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

async function browseAndScreenshot(url, outputPath) {
  console.log('启动 Edge 浏览...');
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/microsoft-edge',
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
  
  // 小黑盒特殊处理：先访问主页，再进社区
  if (isXiaoheihe) {
    console.log('先访问小黑盒主页...');
    await page.goto('https://xiaoheihe.cn', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await new Promise(r => setTimeout(r, 5000));
    await page.evaluate(() => window.scrollBy(0, 100));
    await new Promise(r => setTimeout(r, 2000));
  }
  
  console.log('打开页面: ' + url);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (e) {
    console.log('打开页面失败: ' + e.message);
  }
  
  console.log('正在浏览页面...');
  await new Promise(r => setTimeout(r, 5000));
  
  await page.evaluate(() => {
    window.scrollBy(0, 200);
  });
  await new Promise(r => setTimeout(r, 2000));
  
  let clicked = false;
  let pageTitle = '';
  
  try {
    let selector = null;
    if (isBilibili) {
      selector = 'a[href*="/video/"]';
    } else if (isXiaoheihe) {
      selector = '.hb-cpt__bbs-list-content';
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
          
          await new Promise(r => setTimeout(r, 5000));
          console.log('内容页面加载完成');
          
          // B站自动播放
          if (isBilibili) {
            try {
              const playBtn = await page.evaluateHandle(() => {
                const buttons = Array.from(document.querySelectorAll('button, a, div'));
                return buttons.find(b => b.textContent.includes('立即播放'));
              });
              if (playBtn) {
                console.log('点击立即播放按钮...');
                await playBtn.click();
                await new Promise(r => setTimeout(r, 3000));
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
  
  // 等待页面稳定
  await new Promise(r => setTimeout(r, 2000));
  
  try {
    pageTitle = await page.title();
    console.log('页面标题: ' + pageTitle);
  } catch (e) {
    console.log('提取标题失败');
  }
  
  try {
    await page.evaluate(() => {
      window.scrollBy(0, 200);
    });
  } catch (e) {
    console.log('滚动失败: ' + e.message);
  }
  await new Promise(r => setTimeout(r, 1000));
  
  try {
    await page.screenshot({ path: outputPath, fullPage: false });
    console.log('截图已保存: ' + outputPath);
    if (clicked) console.log('（这是点进去后的内容页面）');
  } catch (e) {
    console.log('截图失败: ' + e.message);
  }
  
  await browser.close();
  
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
