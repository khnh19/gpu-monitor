#!/bin/bash
python3 src/gpu_monitor.py \
    --free_gpu_num 4 \
    --gpu_mem_thresh 2000 \
    --monitor_interval 60 \
    --user_email "your_email" \
    --user_email_password "your_app_password" \
    --host_name "localhost" \
