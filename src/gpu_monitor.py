import argparse
import os
import smtplib
import subprocess
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import GPUtil


def send_email(sender, password, receiver, subject, body):
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())

        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")
        raise


def get_free_gpus(gpu_mem_thresh):
    """Get list of free GPUs."""
    try:
        gpus = GPUtil.getGPUs()
        return [gpu for gpu in gpus if gpu.memoryUsed < gpu_mem_thresh]
    except Exception as e:
        print(f"GPU check failed: {e}")
        return []


def format_gpu_info(gpus):
    """Format GPU information."""
    return "\n".join(
        [f"GPU {gpu.id}: {gpu.memoryUsed:.0f}/{gpu.memoryTotal:.0f} MB" for gpu in gpus]
    )


def execute_script(free_gpus, user_email, password, host_name):
    """Execute the user script with available GPUs."""
    free_gpu_ids = [gpu.id for gpu in free_gpus]

    # Set GPU environment
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, free_gpu_ids))

    # Notify GPU availability
    gpu_info = format_gpu_info(free_gpus)
    send_email(
        user_email,
        password,
        user_email,
        f"GPUs Available on {host_name}",
        f"Free GPUs: {free_gpu_ids}\n\n{gpu_info}",
    )

    # Run script
    script_path = os.getenv("BASH_SCRIPT_PATH", "./my_script.sh")

    try:
        print(f"Running script: {script_path}")
        result = subprocess.run(
            ["bash", script_path], capture_output=True, text=True, timeout=3600
        )

        if result.returncode == 0:
            send_email(
                user_email,
                password,
                user_email,
                f"Execution Successful on {host_name}",
                f"Script completed successfully.\n\nOutput:\n{result.stdout}",
            )
            print("Script completed successfully")
        else:
            send_email(
                user_email,
                password,
                user_email,
                f"Execution Failed on {host_name}",
                f"Script failed with return code {result.returncode}.\n\nError:\n{result.stderr}",
            )
            print("Script failed")

    except subprocess.TimeoutExpired:
        send_email(
            user_email,
            password,
            user_email,
            f"Execution Timeout on {host_name}",
            "Script execution timed out after 1 hour",
        )
        print("Script timed out")
    except Exception as e:
        send_email(
            user_email,
            password,
            user_email,
            f"Execution Error on {host_name}",
            f"Script execution error: {e}",
        )
        print(f"Execution error: {e}")


def monitor(
    free_gpu_num,
    gpu_mem_thresh,
    monitor_interval,
    user_email,
    password,
    host_name,
    test_mode=False,
):
    """Start monitoring GPUs."""

    # Send start notification
    send_email(
        user_email,
        password,
        user_email,
        f"Monitor Started @ {host_name}",
        f"GPU monitoring started on {host_name}\n"
        f"Required free GPUs: {free_gpu_num}\n"
        f"Memory threshold: {gpu_mem_thresh} MB\n"
        f"Check interval: {monitor_interval} seconds",
    )

    print(f"Starting GPU monitor on {host_name}")

    try:
        check_count = 0
        while True:
            check_count += 1
            free_gpus = get_free_gpus(gpu_mem_thresh)
            free_count = len(free_gpus)

            print(f"Check #{check_count}: {free_count} free GPUs")

            if test_mode and free_gpus:
                print("Free GPU Status:")
                print(format_gpu_info(free_gpus))

            if free_count >= free_gpu_num:
                print(f"Found {free_count} free GPUs (need {free_gpu_num})")

                if not test_mode:
                    execute_script(free_gpus, user_email, password, host_name)
                    print("Monitoring completed")
                    break
                else:
                    print("Test mode - would execute script now")

            time.sleep(monitor_interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        send_email(
            user_email,
            password,
            user_email,
            f"Monitor Stopped @ {host_name}",
            "GPU monitoring was stopped by user",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Monitor GPU availability and run scripts"
    )

    parser.add_argument(
        "--free_gpu_num", type=int, default=4, help="Number of free GPUs required"
    )
    parser.add_argument(
        "--gpu_mem_thresh", type=int, default=2000, help="GPU memory threshold in MB"
    )
    parser.add_argument(
        "--monitor_interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds",
    )
    parser.add_argument(
        "--user_email", required=True, help="Email address for notifications"
    )
    parser.add_argument(
        "--user_email_password", required=True, help="Email app password"
    )
    parser.add_argument(
        "--host_name", default="localhost", help="Host name for notifications"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode (no script execution)"
    )

    args = parser.parse_args()

    # Check if script exists (unless test mode)
    script_path = os.getenv("BASH_SCRIPT_PATH", "./my_script.sh")
    if not args.test and not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        print("Set BASH_SCRIPT_PATH environment variable")
        return 1

    monitor(
        args.free_gpu_num,
        args.gpu_mem_thresh,
        args.monitor_interval,
        args.user_email,
        args.user_email_password,
        args.host_name,
        args.test,
    )


if __name__ == "__main__":
    main()
