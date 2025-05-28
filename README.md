# gpu-monitor

A simple Python tool to monitor GPU availability, automatically run your script when enough GPUs are free, and send email notifications at each stage.

## Features

- Monitors GPU memory usage and availability
- Runs a custom script when the required number of GPUs are free
- Sends email notifications for monitoring start, GPU availability, script success, and failure

## Requirements

- Python 3.x
- [GPUtil](https://github.com/anderskm/gputil)

## Installation

```bash
pip3 install GPUtil
```

## Usage

1. Set your script path:

   ```bash
   export BASH_SCRIPT_PATH=/path/to/your_script.sh
   ```

   Default is `my_script.sh`.

2. Make `run.sh` executable:

   ```bash
   chmod +x run.sh
   ```

3. Edit `run.sh` and fill in your email and app password.

4. Start monitoring:
   ```bash
   ./run.sh
   ```

## Configuration

Edit `run.sh` to change parameters:

- `--free_gpu_num`-- Number of free GPUs required (default: 4)
- `--gpu_mem_thresh`-- Max memory usage (MB) to consider a GPU free (default: 2000)
- `--monitor_interval`-- Time between checks (seconds, default: 60)
- `--user_email`-- Your email address (required)
- `--user_email_password`-- Your email app password (required)
- `--host_name`-- Hostname for notifications (default: localhost)

> **Note:** For Gmail, you need to use an **app password** (not your regular email password). See [Google's guide](https://support.google.com/accounts/answer/185833)
