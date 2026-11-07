# 上杉绘梨衣 QQ 机器人

基于 QQagent + SnowLuma 协议端的 QQ 机器人，人设为《龙族》中的上杉绘梨衣。

## 功能特性

- 🤖 拟人化聊天，上杉绘梨衣人设
- 🎤 语音识别（本地 Whisper ASR）
- 👁️ 视觉理解（Gemini 视觉模型）
- 📄 文件读取（TXT/MD/DOCX）
- 🧠 记忆库，自动对话总结
- 🎭 情绪系统，多维度情绪调节
- 💬 主动发言，觉得有意思就分享
- ✅ 自动通过好友申请、自动进群

## 快速部署

```bash
git clone https://github.com/your-username/erii-bot.git
cd erii-bot
sudo bash deploy.sh
```

## 部署后配置

### 1. 编辑主配置

编辑 `config/app.yaml`：
- 填入你的 QQ 号
- 配置 LLM provider 和 model
- 配置视觉模型

### 2. 编辑 Provider 配置

编辑 `config/providers.local.yaml`：
- 填入你的 API key
- 配置可用的模型列表

### 3. 调整人设

编辑 `personas/erii.yaml`：
- 修改性格、说话方式
- 添加记忆和背景故事

## 架构说明

```
QQ 客户端
    ↓ (OneBot WS)
SnowLuma 协议端 (Docker 容器)
    ↓
QQagent (Node.js)
    ├── LLM: DeepSeek V4 Flash / 书生·端砚
    ├── Vision: Gemini 3.8 Flash
    ├── ASR: 本地 Whisper (Flask 9881)
    ├── TTS: Edge TTS
    └── 记忆库: SQLite
```

## 目录结构

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
│   └── local_asr.py       # 本地 Whisper ASR
└── systemd/
    ├── qqagent.service    # QQagent 服务
    └── auto-approve.service # 自动通过服务
```

## 常用命令

```bash
# 查看机器人日志
journalctl -u qqagent -f

# 重启机器人
systemctl restart qqagent

# 查看 SnowLuma 日志
docker logs snowluma

# 查看自动通过好友日志
journalctl -u auto-approve -f
```

## 环境要求

- Ubuntu 22.04+
- 至少 2GB 内存
- Docker
- Node.js 20+
- Python 3.10+

## API 配置

支持的模型 Provider：
- 书生·端砚（inkstone）
- DeepSeek
- OpenRouter
- 77625 路由站（Gemini）
- Groq
- Edge TTS

## License

MIT
