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
      '--window-size=1280,800'
    ]
  });
  
  const page = await browser.newPage();
  
  // 判断是不是 B站，如果是就用手机版
  const isBilibili = url.includes('bilibili.com');
  if (isBilibili) {
    // 手机版 User-Agent
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1');
    await page.setViewport({ width: 375, height: 667 });
    // 改成手机版 URL
    if (url.includes('www.bilibili.com')) {
      url = url.replace('www.bilibili.com', 'm.bilibili.com');
    }
  } else {
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0');
    await page.setViewport({ width: 1280, height: 800 });
  }
  
  console.log('打开页面: ' + url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  console.log('正在浏览页面...');
  await new Promise(r => setTimeout(r, 5000));
  
  // 滚动一下
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
    } else if (url.includes('xiaoheihe.cn')) {
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
        
        // 获取链接地址
        let href = await randomLink.evaluate(el => el.href);
        console.log('原始链接: ' + href);
        
        // 如果是 B站，把链接也改成手机版
        if (isBilibili && href.includes('www.bilibili.com')) {
          href = href.replace('www.bilibili.com', 'm.bilibili.com');
          console.log('改成手机版: ' + href);
        }
        
        // 直接跳转
        await page.goto(href, { 
          waitUntil: 'domcontentloaded', 
          timeout: 20000,
          referer: url
        });
        clicked = true;
        
        await new Promise(r => setTimeout(r, 5000));
        console.log('内容页面加载完成');
      }
    }
  } catch (e) {
    console.log('点击失败，就在首页看看: ' + e.message);
  }
  
  try {
    pageTitle = await page.title();
    console.log('页面标题: ' + pageTitle);
  } catch (e) {
    console.log('提取标题失败');
  }
  
  // 再滚动一下
  await page.evaluate(() => {
    window.scrollBy(0, 200);
  });
  await new Promise(r => setTimeout(r, 1000));
  
  await page.screenshot({ path: outputPath, fullPage: false });
  console.log('截图已保存: ' + outputPath);
  if (clicked) console.log('（这是点进去后的内容页面）');
  
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
