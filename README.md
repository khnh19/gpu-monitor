# gpu-monitor

A tool to monitor free GPUs, automatically run a script when available, and send email notifications.

## Usage

```bash
git clone https://github.com/khnh19/gpu-monitor.git
cd gpu-monitor
pip3 install GPUtil
```

```bash
# optional: only needed if you want to run a script other than my_script.sh
export BASH_SCRIPT_PATH=/path/to/your_script.sh
```

Modify `run.sh` and:

```bash
./run.sh
