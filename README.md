# GPU Monitor

A tool to monitor GPU availability and automatically run scripts when GPUs are free.

## Setup

1. Install requirements:

   ```bash
   pip3 install -r requirements.txt
   ```

2. Set your script path:

   ```bash
   export BASH_SCRIPT_PATH=/path/to/your_script.sh
   ```

3. Edit `run.sh` with your email credentials

4. Run:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## Configuration

Edit `run.sh` parameters:

- `--free_gpu_num` - GPUs needed (default: 4)
- `--gpu_mem_thresh` - Memory threshold MB (default: 2000)
- `--monitor_interval` - Check interval seconds (default: 60)
- `--user_email` - Your email
- `--user_email_password` - Gmail app password

