# gpu-monitor

A script to monitor available GPUs, automatically run a custom script when enough GPUs are free, and send email notifications at each stage.

## Usage

```bash
pip3 install GPUtil
```

```bash
# optional: if you want to run a script other than my_script.sh
export BASH_SCRIPT_PATH=/path/to/your_script.sh
```

Modify `run.sh`, then:

```bash
./run.sh
```
