#!/bin/bash
# 启动完整服务（单端口模式）
# 需要先构建前端：cd web-frontend && npm run build

echo "启动 Red-Stock..."
echo "确保已构建前端：cd web-frontend && npm run build"

# 检查前端构建文件是否存在
if [ ! -d "web-frontend/dist" ]; then
    echo "错误：前端构建文件不存在！"
    echo "请先运行：cd web-frontend && npm install && npm run build"
    exit 1
fi

# 启动Flask服务
echo "启动后端服务（包含前端静态文件）..."
python web-server/app.py



