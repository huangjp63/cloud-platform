#!/bin/bash

# 华为云部署脚本

set -e

echo "开始部署Cloud Platform项目到华为云ECS..."

# 1. 系统环境准备
echo "1. 系统环境准备"
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# 2. 安装Docker
echo "2. 安装Docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 3. 安装Docker Compose
echo "3. 安装Docker Compose"
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 克隆项目代码
echo "4. 克隆项目代码"
if [ -d "Cloud-Platform" ]; then
    cd Cloud-Platform
    git pull
else
    git clone https://github.com/yourusername/Cloud-Platform.git
    cd Cloud-Platform
fi

# 5. 配置环境变量
echo "5. 配置环境变量"
cp deploy/docker/.env.production .env

# 6. 构建和启动服务
echo "6. 构建和启动服务"
sudo docker-compose -f deploy/docker/docker-compose.yml up -d

echo "部署完成！"
echo "请访问 http://$(curl -s ifconfig.me) 查看应用"
