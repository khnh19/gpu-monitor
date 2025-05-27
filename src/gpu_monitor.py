import argparse
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import GPUtil
import subprocess


def send_email(
    sender,
    password,
    receiver,
    subject="Test",
    body="Test",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
):
    # create message
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    # body
    msg.attach(MIMEText(body, "plain"))

    try:
        # connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        # TLS for security
        server.starttls()
        # login
        server.login(sender, password)
        # send email
        server.sendmail(sender, receiver, msg.as_string())
        # close the server
        server.quit()

    except Exception as e:
        raise


def monitor(
    free_gpu_num,
    gpu_mem_thresh,
    func,
    monitor_interval,
    user_email,
    user_email_password,
    host_name,
    once=True,
    test=False,
):
    send_email(
        user_email,
        user_email_password,
        user_email,
        f"Monitor Started @ {host_name}",
        f"Monitoring started on {host_name}...",
    )

    while True:
        # list all GPUs
        gpus = GPUtil.getGPUs()
        # filter based on memory
        free_gpus = [gpu for gpu in gpus if gpu.memoryUsed < gpu_mem_thresh]
        # number of free GPUs
        free_gpu_count = len(free_gpus)

        if test:
            print(f"Free GPUs: {free_gpu_count}")

        if free_gpu_count >= free_gpu_num:
            func(free_gpus, user_email, user_email_password, host_name)

            if once:
                break

        # wait for the next check
        time.sleep(monitor_interval)


def func(free_gpus, user_email, user_email_password, host_name):
    free_gpu_ids = [gpu.id for gpu in free_gpus]

    # environment variable for CUDA
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, free_gpu_ids))

    gpu_info = "\n".join(
        [f"GPU {gpu.id}: {gpu.memoryUsed}/{gpu.memoryTotal} MB" for gpu in free_gpus]
    )

    send_email(
        user_email,
        user_email_password,
        user_email,
        f"GPU(s) Available on {host_name}",
        f"Free GPU(s): {free_gpu_ids}\n\n{gpu_info}",
    )

    # bash script to run
    bash_script_path = os.getenv("BASH_SCRIPT_PATH", "./my_script.sh")

    result = subprocess.run(
        ["bash", bash_script_path],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # result
    if result.returncode == 0:
        send_email(
            user_email,
            user_email_password,
            user_email,
            f"Execution Successful on {host_name}",
            result.stdout.decode(),
        )

    else:
        send_email(
            user_email,
            user_email_password,
            user_email,
            f"Execution Failed on {host_name}",
            result.stderr.decode(),
        )


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Monitor GPU")

    parser.add_argument(
        "--free_gpu_num", type=int, default=4, help="Number of free GPUs"
    )

    parser.add_argument(
        "--gpu_mem_thresh", type=int, default=1000, help="GPU memory threshold in MB"
    )

    parser.add_argument(
        "--monitor_interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds",
    )

    parser.add_argument("--user_email", type=str, required=True, help="User email")

    parser.add_argument(
        "--user_email_password", type=str, required=True, help="User email password"
    )

    parser.add_argument("--host_name", type=str, default="localhost", help="Host name")

    parser.add_argument("--test", action="store_true", help="Run in test mode")

    args = parser.parse_args()

    monitor(
        free_gpu_num=args.free_gpu_num,
        gpu_mem_thresh=args.gpu_mem_thresh,
        func=func,
        monitor_interval=args.monitor_interval,
        user_email=args.user_email,
        user_email_password=args.user_email_password,
        host_name=args.host_name,
        test=args.test,
    )


if __name__ == "__main__":
    main()
