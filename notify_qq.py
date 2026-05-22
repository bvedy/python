#!/usr/bin/env python3
"""
通过QQ邮箱发送每日提醒给 Kenton
用法：python3 notify_qq.py
配置：先设置环境变量 QQ_FROM / QQ_AUTH_CODE / QQ_TO
"""

import smtplib
import os
import sys
import datetime
from email.mime.text import MIMEText
from email.header import Header

# ── 从环境变量读取配置（不要把密码写死在代码里）──
QQ_FROM      = os.environ.get("QQ_FROM", "")       # 你的QQ邮箱，如 123456@qq.com
QQ_AUTH_CODE = os.environ.get("QQ_AUTH_CODE", "")  # QQ邮箱授权码（不是QQ密码）
QQ_TO        = os.environ.get("QQ_TO", "")         # 收件人，填自己的QQ邮箱即可

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587  # STARTTLS


def build_message() -> tuple[str, str]:
    """返回 (主题, 正文)"""
    # 从 kenton_30day_plan 模块拿今日计划文字
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from kenton_30day_plan import (
            get_day_number, get_promotion_countdown,
            DAILY_PLAN, START_DATE
        )

        today = datetime.date.today()
        day_num = get_day_number(today)
        countdown = get_promotion_countdown(today)
        plan = DAILY_PLAN.get(day_num)

        if not plan or day_num < 1 or day_num > 30:
            subject = "Kenton 每日提醒"
            body = f"今天（{today}）不在30天计划范围内，记得照顾好自己。"
            return subject, body

        subject = f"Day {day_num} [{plan['phase']}] | {countdown}"
        body = f"""Kenton，早上好！

今天是30天计划第 {day_num} 天  [{plan['phase']}]
{today.strftime('%Y年%m月%d日')}  |  {countdown}

━━━━━━━━━━━━━━━━━━━━━━
【工作重点】
{plan['work']}

【健康提醒】
{plan['health']}

【管理功课】
{plan['manage']}

━━━━━━━━━━━━━━━━━━━━━━
今晚目标：{plan['tonight']}
━━━━━━━━━━━━━━━━━━━━━━

加油，Kenton。你在进步。
"""
        return subject, body

    except Exception as e:
        return "Kenton 每日提醒", f"今日提醒生成失败：{e}"


def send(subject: str, body: str) -> bool:
    if not QQ_FROM or not QQ_AUTH_CODE or not QQ_TO:
        print("错误：请先设置环境变量 QQ_FROM、QQ_AUTH_CODE、QQ_TO")
        print("运行：python3 notify_qq.py setup  查看配置说明")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"]    = Header(f"Kenton提醒助手 <{QQ_FROM}>")
    msg["To"]      = QQ_TO
    msg["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(QQ_FROM, QQ_AUTH_CODE)
            server.sendmail(QQ_FROM, [QQ_TO], msg.as_string())
        print(f"✓ 已发送：{subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("认证失败：请检查 QQ_AUTH_CODE 是否正确（需要是授权码，不是QQ密码）")
        return False
    except smtplib.SMTPException as e:
        print(f"发送失败：{e}")
        return False
    except Exception as e:
        print(f"网络错误：{e}")
        return False


def print_setup_guide():
    script = os.path.abspath(__file__)
    plan_script = os.path.join(os.path.dirname(script), "kenton_30day_plan.py")

    print("""
════════════════════════════════════════════════════════
  QQ邮箱提醒配置指南
════════════════════════════════════════════════════════

  原理：把每日计划发到你的QQ邮箱（QQ号@qq.com），
        QQ收到邮件会在手机/电脑弹出通知。

  ── 第一步：开启QQ邮箱SMTP服务，获取授权码 ──────────

  1. 电脑打开 mail.qq.com，登录你的QQ邮箱
  2. 点右上角「设置」→「账户」
  3. 往下找「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
  4. 开启「SMTP服务」
  5. 点「生成授权码」，按提示发短信验证
  6. 复制生成的授权码（16位字母，如 abcdefghijklmnop）
     ⚠️ 授权码只显示一次，请立刻保存好

  ── 第二步：设置环境变量 ────────────────────────────

  把以下内容加入你的 ~/.bashrc 或 ~/.zshrc 文件末尾：

    export QQ_FROM="你的QQ号@qq.com"
    export QQ_AUTH_CODE="你的16位授权码"
    export QQ_TO="你的QQ号@qq.com"

  然后执行：
    source ~/.bashrc   （或 source ~/.zshrc）

  ── 第三步：测试发送 ─────────────────────────────────
""")
    print(f"    python3 {script}")
    print("""
  ── 第四步：配置每日定时任务（cron）──────────────────

  执行：crontab -e

  添加以下内容（每天9:00发送，包含环境变量）：
""")
    print(f"  0 9 * * * QQ_FROM=\"你的QQ号@qq.com\" QQ_AUTH_CODE=\"16位授权码\" QQ_TO=\"你的QQ号@qq.com\" python3 {script} >> ~/kenton_notify.log 2>&1")
    print("""
  ── 查看运行日志 ─────────────────────────────────────

    tail -20 ~/kenton_notify.log

════════════════════════════════════════════════════════
  常见问题
════════════════════════════════════════════════════════

  Q: 收不到邮件？
  A: 检查QQ邮箱「垃圾箱」，首次可能被过滤

  Q: 认证失败？
  A: 确认用的是「授权码」而不是QQ登录密码

  Q: 想换个时间？
  A: cron 格式是「分 时 * * *」，如 30 8 表示8:30

════════════════════════════════════════════════════════
""")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        print_setup_guide()
        return

    subject, body = build_message()
    success = send(subject, body)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
