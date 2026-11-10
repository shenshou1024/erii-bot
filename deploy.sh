#!/bin/bash
# 上杉绘梨衣 QQ 机器人一键部署脚本
# 支持 Ubuntu 22.04+

set -e

echo "========================================="
echo "  上杉绘梨衣 QQ 机器人一键部署"
echo "========================================="

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
  echo "请用 root 运行：sudo bash deploy.sh"
  exit 1
fi

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QQAGENT_DIR="/opt/QQagent"
SNOWLUMA_IMAGE="snowluma/snowluma:latest"
WS_PORT=3001
ACCESS_TOKEN="erii2024secretkey"

echo ""
echo "[1/7] 安装系统依赖..."
apt update -y
apt install -y docker.io docker-compose python3 python3-pip git curl wget xdotool ffmpeg

# 安装 Node.js
if ! command -v node &> /dev/null; then
  echo "安装 Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt install -y nodejs
fi

# 安装 Python 依赖
pip3 install websockets faster-whisper flask openai requests beautifulsoup4

echo ""
echo "[2/7] 部署 SnowLuma 协议端..."
docker pull $SNOWLUMA_IMAGE

# 创建数据目录
mkdir -p /var/snowluma/data

# 启动 SnowLuma 容器
docker run -d \
  --name snowluma \
  --restart always \
  -p 127.0.0.1:$WS_PORT:3001 \
  -v /var/snowluma/data:/app/data \
  -e WS_PORT=3001 \
  -e ACCESS_TOKEN=$ACCESS_TOKEN \
  $SNOWLUMA_IMAGE

echo "SnowLuma 容器已启动"

echo ""
echo "[3/7] 安装 QQagent..."
if [ ! -d "$QQAGENT_DIR" ]; then
  git clone https://github.com/your-username/QQagent.git $QQAGENT_DIR
fi

cd $QQAGENT_DIR
npm install

echo ""
echo "[4/7] 复制配置文件和脚本..."
# 复制配置
mkdir -p config/personas
cp $SCRIPT_DIR/config/app.yaml config/app.yaml
cp $SCRIPT_DIR/config/providers.local.yaml config/providers.local.yaml
cp $SCRIPT_DIR/personas/erii.yaml config/personas/erii.yaml

# 复制脚本
mkdir -p scripts
cp $SCRIPT_DIR/scripts/*.py scripts/

echo ""
echo "[5/7] 配置 systemd 服务..."
# QQagent 服务
cat > /etc/systemd/system/qqagent.service << EOF
[Unit]
Description=QQ Agent (Erii Persona)
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$QQAGENT_DIR
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5
Environment=HF_ENDPOINT=https://hf-mirror.com

[Install]
WantedBy=multi-user.target
EOF

# 自动通过好友服务
cat > /etc/systemd/system/auto-approve.service << EOF
[Unit]
Description=QQ Auto Approve Friend and Group Requests
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$QQAGENT_DIR
ExecStart=/usr/bin/python3 scripts/auto_approve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 本地 ASR 服务
cat > /etc/systemd/system/local-asr.service << EOF
[Unit]
Description=Local Whisper ASR Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$QQAGENT_DIR
ExecStart=/usr/bin/python3 scripts/local_asr.py
Restart=always
RestartSec=5
Environment=HF_ENDPOINT=https://hf-mirror.com

[Install]
WantedBy=multi-user.target
EOF

# TTS 服务
cat > /etc/systemd/system/tts-server.service << EOF
[Unit]
Description=Edge TTS Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$QQAGENT_DIR
ExecStart=/usr/bin/python3 scripts/tts_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 注意：网页截图服务（proactive-screenshot）在 v0.2.3 起默认禁用，
# 原因：与 QQagent 同时连接同一 OneBot WebSocket 存在多客户端冲突，
# 且偶发崩溃重启占用资源。源码保留在 scripts/ 与 systemd/ 中，
# 待问题修复后可手动启用，不在此自动创建/启动。

systemctl daemon-reload

echo ""
echo "[6/7] 启动服务..."
systemctl enable --now qqagent
systemctl enable --now auto-approve
systemctl enable --now local-asr
systemctl enable --now tts-server

echo ""
echo "[7/7] 完成！"
echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "功能列表："
echo "  - 拟人化聊天（上杉绘梨衣人设）"
echo "  - 语音识别（本地 Whisper ASR）"
echo "  - 视觉理解（Gemini 视觉模型）"
echo "  - 文件读取（TXT/MD/DOCX）"
echo "  - 音乐播放（alisten_music）"
echo "  - 网页搜索（web_search）"
echo "  - QQ空间发帖（qzone_post）"
echo "  - 记忆库，自动对话总结"
echo "  - 情绪系统，多维度情绪调节"
echo "  - 主动发言，觉得有意思就分享"
echo "  - 自动通过好友申请、自动进群"
echo "  （网页截图功能 v0.2.3 起暂时禁用，详见 README）"
echo ""
echo "下一步："
echo "1. 查看 SnowLuma 日志：docker logs snowluma"
echo "2. 扫码登录 QQ（通过 noVNC）"
echo "3. 查看 QQagent 日志：journalctl -u qqagent -f"
echo ""
echo "注意："
echo "- 请编辑 config/app.yaml 填入你的 API key"
echo "- 请编辑 config/providers.local.yaml 配置你的模型"
echo "- 请编辑 personas/erii.yaml 调整人设"
echo ""
