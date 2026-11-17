const WebSocket = require('ws');

const WS_URL = 'ws://127.0.0.1:3001';
const TOKEN = 'erii2024secretkey';
const TARGET_QQ = 1701793763;

// 随机消息模板（绘梨衣风格）
const messages = [
  'Sakura 在干嘛',
  '有点想 Sakura',
  'Sakura 理理我',
  '……无聊',
  'Sakura 吃了吗',
  'Sakura 在忙吗',
  'Sakura 最好了',
  '好无聊啊',
  'Sakura 今天开心吗',
  '在想 Sakura',
];

// ============ 晚安静默（与主框架 goodnight.ts 行为一致） ============
// - 目标私聊发来晚安等关键词 → 静默，暂停主动私聊推送
// - 发来其他正常消息 → 解除静默
// - 兜底：进入静默后到下一个 20:00（晚上八点）自动解除
const GOODNIGHT_RE = /晚安|睡啦|睡了|去睡|睡觉啦|休息了|先睡/;

let muted = false;
let enterAt = 0;

function restoreAt(enter) {
  const restore = new Date(enter);
  restore.setHours(20, 0, 0, 0);
  if (restore.getTime() <= enter) {
    restore.setDate(restore.getDate() + 1);
  }
  return restore.getTime();
}

function isMuted(now = Date.now()) {
  if (!muted) return false;
  if (now >= restoreAt(enterAt)) {
    muted = false;
    return false;
  }
  return true;
}

function observe(text) {
  const t = (text || '').trim();
  if (!t) return;
  if (GOODNIGHT_RE.test(t)) {
    muted = true;
    enterAt = Date.now();
    console.log('🌙 收到晚安，进入静默，暂停主动私聊');
  } else if (muted) {
    muted = false;
    console.log('💬 开始聊天，解除晚安静默');
  }
}

function extractText(ev) {
  if (typeof ev.raw_message === 'string' && ev.raw_message.trim()) return ev.raw_message;
  if (typeof ev.message === 'string') return ev.message;
  return '';
}
// ====================================================================

function connect() {
  const ws = new WebSocket(WS_URL, {
    headers: { Authorization: `Bearer ${TOKEN}` }
  });

  ws.on('open', () => {
    console.log('Connected to OneBot');
    scheduleMessage(ws);
  });

  ws.on('message', (data) => {
    let ev;
    try { ev = JSON.parse(data); } catch { return; }
    // 只关心目标私聊的入站消息，用于更新晚安状态
    if (ev.post_type === 'message' && ev.message_type === 'private' && Number(ev.user_id) === TARGET_QQ) {
      observe(extractText(ev));
    }
  });

  ws.on('close', () => {
    console.log('Disconnected, reconnecting in 5s...');
    setTimeout(connect, 5000);
  });

  ws.on('error', (err) => {
    console.error('WS error:', err.message);
  });
}

function scheduleMessage(ws) {
  // 随机 1-3 小时发一条
  const delay = (30 + Math.random() * 60) * 60 * 1000;
  console.log(`Next message in ${Math.round(delay / 3600000)} hours`);

  setTimeout(() => {
    if (ws.readyState === WebSocket.OPEN) {
      if (isMuted()) {
        console.log('🌙 晚安静默中，跳过本次主动私聊');
      } else {
        const msg = messages[Math.floor(Math.random() * messages.length)];
        ws.send(JSON.stringify({
          action: 'send_private_msg',
          params: {
            user_id: TARGET_QQ,
            message: msg
          }
        }));
        console.log(`Sent: ${msg}`);
      }
    }
    scheduleMessage(ws);
  }, delay);
}

connect();
