# 上杉绘梨衣 QQ 机器人

基于 QQagent + SnowLuma 协议端的 QQ 机器人，人设为《龙族》中的上杉绘梨衣。

> "Sakura 最好了。" —— 上杉绘梨衣

---

## ✨ 功能特性

### 🤖 核心聊天
- **拟人化人设**：上杉绘梨衣人设，安静、单纯、黏人，称呼信任的人为 Sakura
- **多人格支持**：内置 8 种人格，可随时切换
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

### 3. 调整人设

编辑 `personas/erii.yaml`，修改性格、说话方式、记忆背景等。

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
│   └── qzone_post.py      # QQ空间发帖
└── systemd/
    ├── qqagent.service    # QQagent 服务
    ├── auto-approve.service # 自动通过服务
    ├── local-asr.service  # 本地 ASR 服务
    └── tts-server.service  # TTS 服务
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
