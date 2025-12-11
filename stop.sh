#!/bin/bash
# 停止前后端服务

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件目录
LOG_DIR="$SCRIPT_DIR/logs"
FRONTEND_PID="$LOG_DIR/frontend.pid"
BACKEND_PID="$LOG_DIR/backend.pid"

echo -e "${BLUE}正在停止服务...${NC}"

# 停止前端
if [ -f "$FRONTEND_PID" ]; then
    FRONTEND_PID_VALUE=$(cat "$FRONTEND_PID")
    if ps -p "$FRONTEND_PID_VALUE" > /dev/null 2>&1; then
        echo -e "${BLUE}停止前端服务 (PID: $FRONTEND_PID_VALUE)${NC}"
        kill "$FRONTEND_PID_VALUE" 2>/dev/null || true
        sleep 1
        # 如果还在运行，强制杀死
        if ps -p "$FRONTEND_PID_VALUE" > /dev/null 2>&1; then
            kill -9 "$FRONTEND_PID_VALUE" 2>/dev/null || true
        fi
    fi
    rm -f "$FRONTEND_PID"
fi

# 停止后端
if [ -f "$BACKEND_PID" ]; then
    BACKEND_PID_VALUE=$(cat "$BACKEND_PID")
    if ps -p "$BACKEND_PID_VALUE" > /dev/null 2>&1; then
        echo -e "${BLUE}停止后端服务 (PID: $BACKEND_PID_VALUE)${NC}"
        kill "$BACKEND_PID_VALUE" 2>/dev/null || true
        sleep 1
        # 如果还在运行，强制杀死
        if ps -p "$BACKEND_PID_VALUE" > /dev/null 2>&1; then
            kill -9 "$BACKEND_PID_VALUE" 2>/dev/null || true
        fi
    fi
    rm -f "$BACKEND_PID"
fi

# 清理可能残留的进程
echo -e "${BLUE}清理残留进程...${NC}"
pkill -f "vite" 2>/dev/null || true
pkill -f "web-server/app.py" 2>/dev/null || true

echo -e "${GREEN}服务已停止${NC}"

