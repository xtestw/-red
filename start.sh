#!/bin/bash
# 同时启动前后端服务
# 用法: ./start.sh [--build] [--no-frontend] [--no-backend]

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

# 日志文件
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"

# PID文件
FRONTEND_PID="$LOG_DIR/frontend.pid"
BACKEND_PID="$LOG_DIR/backend.pid"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在停止服务...${NC}"
    
    # 停止前端
    if [ -f "$FRONTEND_PID" ]; then
        FRONTEND_PID_VALUE=$(cat "$FRONTEND_PID")
        if ps -p "$FRONTEND_PID_VALUE" > /dev/null 2>&1; then
            echo -e "${BLUE}停止前端服务 (PID: $FRONTEND_PID_VALUE)${NC}"
            kill "$FRONTEND_PID_VALUE" 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID"
    fi
    
    # 停止后端
    if [ -f "$BACKEND_PID" ]; then
        BACKEND_PID_VALUE=$(cat "$BACKEND_PID")
        if ps -p "$BACKEND_PID_VALUE" > /dev/null 2>&1; then
            echo -e "${BLUE}停止后端服务 (PID: $BACKEND_PID_VALUE)${NC}"
            kill "$BACKEND_PID_VALUE" 2>/dev/null || true
        fi
        rm -f "$BACKEND_PID"
    fi
    
    # 清理可能残留的进程
    pkill -f "vite" 2>/dev/null || true
    pkill -f "web-server/app.py" 2>/dev/null || true
    
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 解析参数
BUILD_FRONTEND=false
START_FRONTEND=true
START_BACKEND=true

for arg in "$@"; do
    case $arg in
        --build)
            BUILD_FRONTEND=true
            shift
            ;;
        --no-frontend)
            START_FRONTEND=false
            shift
            ;;
        --no-backend)
            START_BACKEND=false
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  --build           启动前先构建前端"
            echo "  --no-frontend     不启动前端服务"
            echo "  --no-backend      不启动后端服务"
            echo "  --help, -h        显示帮助信息"
            exit 0
            ;;
        *)
            echo -e "${RED}未知参数: $arg${NC}"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 检查并构建前端
if [ "$BUILD_FRONTEND" = true ]; then
    echo -e "${BLUE}构建前端...${NC}"
    cd "$SCRIPT_DIR/web-frontend"
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装前端依赖...${NC}"
        npm install
    fi
    npm run build
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}前端构建完成${NC}"
fi

# 启动后端服务
if [ "$START_BACKEND" = true ]; then
    echo -e "${BLUE}启动后端服务...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}错误: 未找到Python${NC}"
        exit 1
    fi
    
    # 检查后端文件
    if [ ! -f "web-server/app.py" ]; then
        echo -e "${RED}错误: 后端文件不存在: web-server/app.py${NC}"
        exit 1
    fi
    
    # 启动后端（后台运行）
    if command -v python3 &> /dev/null; then
        nohup python3 web-server/app.py > "$BACKEND_LOG" 2>&1 &
    else
        nohup python web-server/app.py > "$BACKEND_LOG" 2>&1 &
    fi
    
    BACKEND_PID_VALUE=$!
    echo "$BACKEND_PID_VALUE" > "$BACKEND_PID"
    echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID_VALUE)${NC}"
    echo -e "${BLUE}后端日志: $BACKEND_LOG${NC}"
    
    # 等待后端启动
    sleep 2
    
    # 检查后端是否正常运行
    if ! ps -p "$BACKEND_PID_VALUE" > /dev/null 2>&1; then
        echo -e "${RED}错误: 后端服务启动失败${NC}"
        echo -e "${YELLOW}查看日志: tail -f $BACKEND_LOG${NC}"
        exit 1
    fi
fi

# 启动前端服务
if [ "$START_FRONTEND" = true ]; then
    echo -e "${BLUE}启动前端服务...${NC}"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: 未找到Node.js${NC}"
        echo -e "${YELLOW}提示: 如果只需要后端服务，可以使用 --no-frontend 参数${NC}"
        if [ "$START_BACKEND" = true ]; then
            echo -e "${YELLOW}后端服务已启动，前端服务跳过${NC}"
        else
            exit 1
        fi
    else
        cd "$SCRIPT_DIR/web-frontend"
        
        # 检查node_modules
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}安装前端依赖...${NC}"
            npm install
        fi
        
        # 启动前端开发服务器（后台运行）
        nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
        FRONTEND_PID_VALUE=$!
        echo "$FRONTEND_PID_VALUE" > "$FRONTEND_PID"
        echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID_VALUE)${NC}"
        echo -e "${BLUE}前端日志: $FRONTEND_LOG${NC}"
        
        cd "$SCRIPT_DIR"
        
        # 等待前端启动
        sleep 3
    fi
fi

# 显示服务信息
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}服务启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"

if [ "$START_BACKEND" = true ]; then
    echo -e "${BLUE}后端服务:${NC}"
    echo -e "  - API地址: ${GREEN}http://localhost:5000${NC}"
    echo -e "  - 日志文件: $BACKEND_LOG"
    echo -e "  - PID: $(cat "$BACKEND_PID")"
fi

if [ "$START_FRONTEND" = true ] && [ -f "$FRONTEND_PID" ]; then
    echo -e "${BLUE}前端服务:${NC}"
    echo -e "  - 访问地址: ${GREEN}http://localhost:5173${NC}"
    echo -e "  - 日志文件: $FRONTEND_LOG"
    echo -e "  - PID: $(cat "$FRONTEND_PID")"
fi

echo ""
echo -e "${YELLOW}提示:${NC}"
echo -e "  - 查看日志: tail -f $LOG_DIR/*.log"
echo -e "  - 停止服务: 按 Ctrl+C 或运行 ./stop.sh"
echo -e "  - 查看帮助: ./start.sh --help"
echo ""

# 实时显示日志
if [ "$START_BACKEND" = true ] && [ "$START_FRONTEND" = true ]; then
    echo -e "${BLUE}实时日志 (按 Ctrl+C 停止):${NC}"
    tail -f "$BACKEND_LOG" "$FRONTEND_LOG" 2>/dev/null || {
        # 如果tail -f不支持多个文件，分别显示
        echo -e "${YELLOW}提示: 使用以下命令查看日志:${NC}"
        echo -e "  tail -f $BACKEND_LOG  # 后端日志"
        echo -e "  tail -f $FRONTEND_LOG  # 前端日志"
        # 等待用户中断
        while true; do
            sleep 1
        done
    }
elif [ "$START_BACKEND" = true ]; then
    echo -e "${BLUE}实时日志 (按 Ctrl+C 停止):${NC}"
    tail -f "$BACKEND_LOG"
elif [ "$START_FRONTEND" = true ] && [ -f "$FRONTEND_PID" ]; then
    echo -e "${BLUE}实时日志 (按 Ctrl+C 停止):${NC}"
    tail -f "$FRONTEND_LOG"
fi

