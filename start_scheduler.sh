#!/bin/bash
# 启动定时任务调度器
# 用法: ./start_scheduler.sh [--run-now|--immediate]

cd "$(dirname "$0")"
python server/scheduler.py "$@"

