#!/bin/bash
# 启动前端开发服务器

cd "$(dirname "$0")"

# 检查Python是否可用
if command -v python3 &> /dev/null; then
    echo "启动前端开发服务器 (Python HTTP Server)..."
    echo "访问地址: http://localhost:8080"
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "启动前端开发服务器 (Python HTTP Server)..."
    echo "访问地址: http://localhost:8080"
    python -m http.server 8080
else
    echo "错误: 未找到Python，请安装Python或使用Node.js http-server"
    exit 1
fi



