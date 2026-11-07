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
QQAGENT_DIR="/opt/QQagent"
SNOWLUMA_IMAGE="snowluma/snowluma:latest"
WS_PORT=3001
ACCESS_TOKEN="erii2024secretkey"

echo ""
echo "[1/6] 安装系统依赖..."
apt update -y
apt install -y docker.io docker-compose python3 python3-pip git curl wget xdotool

# 安装 Node.js
if ! command -v node &> /dev/null; then
  echo "安装 Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt install -y nodejs
fi

# 安装 Python 依赖
pip3 install websockets faster-whisper flask openai

echo ""
echo "[2/6] 部署 SnowLuma 协议端..."
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
echo "[3/6] 安装 QQagent..."
if [ ! -d "$QQAGENT_DIR" ]; then
  git clone https://github.com/your-username/QQagent.git $QQAGENT_DIR
fi

cd $QQAGENT_DIR
npm install

echo ""
echo "[4/6] 配置文件..."
# 复制配置文件
mkdir -p config/personas
cp /opt/QQagent/config/app.yaml config/app.yaml 2>/dev/null || true
cp /opt/QQagent/config/providers.local.yaml config/providers.local.yaml 2>/dev/null || true
cp /opt/QQagent/config/personas/erii.yaml config/personas/erii.yaml 2>/dev/null || true

# 如果没有配置文件，从模板复制
if [ ! -f config/app.yaml ]; then
  echo "请编辑 config/app.yaml 填入你的配置"
fi

echo ""
echo "[5/6] 配置 systemd 服务..."
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

systemctl daemon-reload

echo ""
echo "[6/6] 启动服务..."
systemctl enable --now qqagent
systemctl enable --now auto-approve

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
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
