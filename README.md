# 上杉绘梨衣 QQ 机器人

基于 QQagent + SnowLuma 协议端的 QQ 机器人，人设为《龙族》中的上杉绘梨衣。

> "Sakura 最好了。" —— 上杉绘梨衣

**✨ 完全可以自定义人设！** 打开 `personas/erii.yaml`，改成你想要的任何角色、任何说话风格，一键部署就能用。

---

## 📝 更新日志

### v0.2.1 (2026-11-08)

**新增功能：**
- ▶️ **B站自动播放**：进入视频页面后，自动点击"立即播放"按钮，真正看视频
- 🎮 **小黑盒防验证码**：先访问小黑盒主页，停留一会，再进社区，避免触发点选验证码

**修复：**
- 🐛 修复被动截图不触发的问题：之前只匹配"截图"两个字，现在说"截个小黑盒的图"也能触发了
- 🐛 优化了错误处理，避免页面 frame 分离导致截图失败

---

### v0.2 (2026-11-08)

**新增功能：**
- 🖼️ **网页截图系统**：机器人自主浏览网页，看到有意思的就截图分享
- 📱 **手机版 B站支持**：用手机版 B站（m.bilibili.com）绕过反爬，可以正常点进视频页面
- 🎮 **小黑盒社区**：直接进入社区刷帖子，点进帖子看内容
- 🎮 **4399 小游戏**：点进游戏详情页
- 🎲 **概率分配系统**：自定义各平台出现概率（B站 30%、小黑盒 25%、小说 15%、其他 20%、休息 10%）
- 🌙 **晚安模式**：发"晚安"暂停所有主动功能，开始聊天自动恢复
- 🧹 **自动清理**：发完截图自动删除临时文件
- 💬 **被动截图指令**：你说"截图"，它立刻截一张给你

**优化：**
- ✅ 清理了所有测试脚本
- ✅ 优化了内存使用
- ✅ 服务时间错开，避免同时发消息打扰

**修复：**
- 🐛 修复 B站视频页面跳转显示"出错啦"的问题：点击视频链接时，自动把链接改成手机版（m.bilibili.com），绕过反爬

---

### v0.1 (2026-11-07)

**初始版本：**
- 🤖 拟人化聊天（上杉绘梨衣人设）
- 🎤 语音识别（本地 Whisper ASR）
- 👁️ 视觉理解（Gemini 视觉模型）
- 📄 文件读取（TXT/MD/DOCX）
- 🎵 音乐播放
- 🔍 网页搜索
- 📝 QQ空间发帖
- 🧠 记忆库，自动对话总结
- 🎭 情绪系统，多维度情绪调节
- 💬 主动发言，觉得有意思就分享
- ✅ 自动通过好友申请、自动进群
- 🗣️ TTS 语音合成（Edge TTS）

---

## ✨ 功能特性

### 🤖 核心聊天
- **拟人化人设**：上杉绘梨衣人设，安静、单纯、黏人，称呼信任的人为 Sakura
- **多人格支持**：内置 8 种人格，可随时切换
- **自定义人设**：完全可以自己改！打开 `personas/erii.yaml`，修改系统提示词、说话风格、触发关键词，变成你想要的任何角色
- **情绪系统**：多维度情绪调节（开心、难过、生气、焦虑等），影响说话方式
- **主动发言**：觉得有意思就主动分享，不用等你问

### 🎙️ 多媒体能力
- **语音识别**：本地 Whisper ASR，免费、快速、隐私
- **语音合成**：Edge TTS，自然的语音输出
- **视觉理解**：Gemini 视觉模型，能看懂图片内容
- **音乐播放**：想听什么歌直接说，机器人给你找

### 📄 文件处理
- **TXT 文件读取**：直接发小说给它，它能看完和你讨论剧情
- **MD/DOCX 支持**：多种文档格式
- **智能分段**：长文件自动总结，不占用太多上下文

### 🧠 记忆系统
- **长期记忆**：记住你说过的话、你的偏好、你的喜好
- **自动总结**：对话太长自动总结，节省 token
- **事实提取**：自动提取关键信息，下次聊天还记得

### 🛠️ 实用工具
- **网页搜索**：想知道什么直接问，机器人帮你搜
- **QQ空间发帖**：可以帮你发空间说说
- **自动通过好友**：别人加你自动通过
- **自动进群**：别人拉你进群自动同意

### 🖼️ 网页截图（v0.2 新增）
- **主动浏览截图**：机器人自己刷网页，看到有意思的就截图分享给你
- **被动截图指令**：你说"截图"，它立刻截一张当前浏览的网页给你
- **智能浏览**：用 Edge 浏览器真实浏览，会点进视频、帖子看内容
- **多平台支持**：B站（手机版）、小黑盒社区、4399、小说网站、豆瓣、知乎、微博、抖音等
- **概率分配**：可自定义各平台出现概率（小黑盒 25%、B站 30%、小说 15%、其他 20%、休息 10%）
- **晚安模式**：你发"晚安"，自动暂停所有主动功能；你开始聊天，自动恢复
- **自动清理**：发完截图自动删除临时文件，不占空间

---

## 🚀 快速部署

```bash
git clone https://github.com/shenshou1024/erii-bot.git
cd erii-bot
sudo bash deploy.sh
```

部署完成后，扫码登录 QQ 就可以用了。

---

## ⚙️ 部署后配置

### 1. 编辑主配置

编辑 `config/app.yaml`：
```yaml
llm:
  defaultProvider: your-provider
  defaultModel: your-model
```

### 2. 编辑 Provider 配置

编辑 `config/providers.local.yaml`，填入你的 API key：
```yaml
providers:
  your-provider:
    apiKey: your-api-key
    baseURL: https://api.example.com/v1
```

### 3. 自定义人设

编辑 `personas/erii.yaml`，可以自定义：

```yaml
# 基本信息
name: 你的人设名字
emoji: "🎭"
description: 人设简介
temperature: 0.95  # 越高越随机，越低越稳定
maxTokens: 300

# 系统提示词（核心！）
systemPrompt: |
  你是XXX，性格XXX...
  【说话方式】
  - 像真人聊天
  - 短句为主
  - 不要句尾加句号

# 戳一戳回复
pokeReplies:
  - 嗯？
  - 干嘛

# 触发关键词
triggers:
  keywords: ["关键词1", "关键词2"]
  command: "/你的命令"
```

**内置多人格：**
- 蓝色大肥鱼 🐋
- 猫娘 🐱
- 冷酷助手 🖤
- 上杉绘梨衣 🐍
- 元气少女 ⚡
- 温柔姐姐 🌙
- 博学学者 📚
- 傲娇 😤

可以在 `config/app.yaml` 里切换默认人设：
```yaml
persona:
  default: erii  # 改成你想要的人设 ID
```

---

## 🏗️ 架构说明

```
QQ 客户端
    ↓ (OneBot WS)
SnowLuma 协议端 (Docker 容器)
    ↓
QQagent (Node.js)
    ├── LLM: DeepSeek V4 Flash / 书生·端砚 / OpenRouter
    ├── Vision: Gemini 3.8 Flash
    ├── ASR: 本地 Whisper (Flask 9881)
    ├── TTS: Edge TTS
    ├── 音乐: alisten_music.py
    ├── 搜索: web_search.py
    ├── 空间: qzone_post.py
    └── 记忆库: SQLite
```

---

## 📁 目录结构

```
erii-bot/
├── deploy.sh              # 一键部署脚本
├── README.md              # 本文件
├── config/
│   ├── app.yaml           # 主配置
│   └── providers.local.yaml  # API 配置
├── personas/
│   └── erii.yaml          # 上杉绘梨衣人设
├── scripts/
│   ├── auto_approve.py    # 自动通过好友/进群
│   ├── local_asr.py       # 本地 Whisper ASR
│   ├── tts_server.py      # TTS 服务
│   ├── alisten_music.py   # 音乐播放
│   ├── web_search.py      # 网页搜索
│   ├── qzone_post.py      # QQ空间发帖
│   ├── web_browse.cjs     # 网页浏览截图（v0.2 新增）
│   └── proactive_screenshot.py # 主动截图发送（v0.2 新增）
└── systemd/
    ├── qqagent.service    # QQagent 服务
    ├── auto-approve.service # 自动通过服务
    ├── local-asr.service  # 本地 ASR 服务
    ├── tts-server.service  # TTS 服务
    └── proactive-screenshot.service # 主动截图服务（v0.2 新增）
```

---

## 📝 常用命令

```bash
# 查看机器人日志
journalctl -u qqagent -f

# 重启机器人
systemctl restart qqagent

# 查看 SnowLuma 日志
docker logs snowluma

# 查看自动通过好友日志
journalctl -u auto-approve -f

# 查看 ASR 服务日志
journalctl -u local-asr -f

# 查看 TTS 服务日志
journalctl -u tts-server -f
```

---

## 📋 环境要求

- Ubuntu 22.04+
- 至少 2GB 内存
- Docker
- Node.js 20+
- Python 3.10+
- ffmpeg

---

## 🔌 支持的模型 Provider

- 书生·端砚（inkstone）
- DeepSeek
- OpenRouter
- 77625 路由站（Gemini）
- Groq
- Edge TTS

---

## 📄 License

MIT

---

## 💖 致谢

- [QQagent](https://github.com/your-username/QQagent) - 机器人框架
- [SnowLuma](https://github.com/your-username/SnowLuma) - OneBot 协议端
- 《龙族》- 上杉绘梨衣人设来源



---

### v0.2.2 (2026-11-08)

**修复：**
- 🐛 修复小黑盒截图 frame 分离导致失败的问题
- 🐛 优化错误处理，点击失败时自动降级为截首页
- 🐛 修复 WebSocket 连接断开后自动重连的稳定性
- 🐛 修复被动截图触发条件，说"截个XX的图"也能触发

**优化：**
- ✅ 优化小黑盒访问逻辑：先访问主页再进社区，避免触发验证码
- ✅ 优化 B站手机版支持，自动点击"立即播放"按钮
- ✅ 优化 systemd 服务配置，QQagent 重启后自动重连
