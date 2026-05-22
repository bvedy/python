#!/usr/bin/env python3
"""
Kenton 30天工作生活平衡规划
考虑618大促节奏，起始日期：2026-05-22
"""

import datetime
import sys
import os

START_DATE = datetime.date(2026, 5, 22)
PROMOTION_DATE = datetime.date(2026, 6, 18)  # 618大促

# ─────────────────────────────────────────────
# 30天每日计划
# ─────────────────────────────────────────────

DAILY_PLAN = {
    # ══════════════════════════════
    # 第一阶段：大促预热期（Day 1-10，5/22-5/31）
    # 核心：理清战场，建立底线
    # ══════════════════════════════
    1: {
        "phase": "预热期",
        "work": "列出大促期间所有你需要亲自负责的工作，其余全部授权",
        "health": "今天开始记录你的睡眠时间，不要求改变，只是记录",
        "manage": "和你的上级约好：大促期间你的工作边界和决策权限是什么",
        "tonight": "21:30之前离开办公室（今天开始设红线）",
    },
    2: {
        "phase": "预热期",
        "work": "梳理虚假品牌塑造大促专项：哪些商家在大促前需要重点审查？",
        "health": "午休15分钟，哪怕闭眼也算",
        "manage": "召集团队：明确大促期间每人的核心职责，写清楚不要靠口头",
        "tonight": "今晚不带笔记本回家",
    },
    3: {
        "phase": "预热期",
        "work": "建立大促期间的'快速响应'SOP，减少临时判断消耗",
        "health": "今天走路上下楼梯替代电梯，积累步数",
        "manage": "识别团队中压力最大的那个人，今天单独聊5分钟",
        "tonight": "22:00之前到家，不谈判",
    },
    4: {
        "phase": "预热期",
        "work": "检查大促商品抽查计划是否就绪，不要等到临近才发现漏洞",
        "health": "喝够8杯水（高压期身体脱水会加重疲惫感）",
        "manage": "今天开一个会之前先问：这个会能用一条消息替代吗？",
        "tonight": "给自己今晚预留30分钟不看手机",
    },
    5: {
        "phase": "预热期",
        "work": "和数据团队确认大促期间监控指标的报警阈值",
        "health": "今天做10分钟拉伸，颈椎、腰背为主",
        "manage": "回顾本周团队完成了什么，发一条肯定信息给团队",
        "tonight": "今晚早睡1小时，哪怕睡不着也要躺着",
    },
    6: {
        "phase": "预热期",
        "work": "本周工作复盘：哪些事其实不需要你做？下周把它们从你的清单划掉",
        "health": "周末补觉：今晚目标8小时",
        "manage": "今天不处理工作消息（如果做到了，说明你边界管理开始生效）",
        "tonight": "给自己做一顿正经的饭，或者点一顿好的",
    },
    7: {
        "phase": "预热期",
        "work": "预演大促期间可能出现的3个最坏场景，提前准备应对预案",
        "health": "出门散步30分钟，不带耳机，让大脑休息",
        "manage": "阅读30分钟管理类书籍（推荐：《高效能人士的七个习惯》第三章）",
        "tonight": "今晚不设工作闹钟",
    },
    8: {
        "phase": "预热期",
        "work": "大促期间的决策流：哪些问题由你决，哪些由团队成员决，写成文档",
        "health": "今天量一次血压（如果没有血压计，今天买一个）",
        "manage": "和一位你信任的管理者前辈聊聊，不需要议题，就是交流",
        "tonight": "21:30离开，无例外",
    },
    9: {
        "phase": "预热期",
        "work": "确认大促期间人员排班：值班覆盖是否有漏洞？",
        "health": "今天注意吃早饭，不管多忙",
        "manage": "把你下周的会议砍掉三分之一（合并或取消）",
        "tonight": "睡前写下3件今天做得好的事（哪怕很小）",
    },
    10: {
        "phase": "预热期",
        "work": "大促准备最后检查：清单过一遍，缺什么今天补",
        "health": "第一阶段复盘：过去10天你的平均睡眠和下班时间是多少？",
        "manage": "告诉团队：大促期间遇到不确定情况，先执行SOP，不要等你审批",
        "tonight": "今晚好好睡，明天进入冲刺模式",
    },

    # ══════════════════════════════
    # 第二阶段：大促冲刺期（Day 11-27，6/1-6/17）
    # 核心：聚焦核心，保住底线，接受高强度
    # ══════════════════════════════
    11: {
        "phase": "冲刺期",
        "work": "大促冲刺正式开始。今天只做最重要的一件事：确保团队状态OK",
        "health": "冲刺期睡眠底线：6.5小时，这是不可妥协的最低值",
        "manage": "每天晨会控制在15分钟以内，只讲今日重点和风险",
        "tonight": "接受今天可能晚一些，但不超过23:00",
    },
    12: {
        "phase": "冲刺期",
        "work": "重点盯高风险商家，非核心审查交给团队处理",
        "health": "今天在办公室做5分钟深呼吸练习，减少焦虑积累",
        "manage": "如果团队成员犯了小错，今天不追责，大促结束后再复盘",
        "tonight": "不管几点到家，先洗个澡再看手机",
    },
    13: {
        "phase": "冲刺期",
        "work": "S级高风险商品今天过一遍，确保处置到位",
        "health": "午饭不在工位吃，换个地方，给眼睛和大脑换环境",
        "manage": "今天主动给一个团队成员说一句：'你做得很好'",
        "tonight": "睡前不看工作消息，哪怕30分钟也行",
    },
    14: {
        "phase": "冲刺期",
        "work": "大促商品投诉量开始上升，检查消费者申诉处理速度是否达标",
        "health": "今天喝够水，高压状态容易忘记喝水",
        "manage": "冲刺第四天，团队情绪可能开始下滑，今天做一次团队鼓励",
        "tonight": "目标23:00前到家",
    },
    15: {
        "phase": "冲刺期",
        "work": "本周进度回顾：哪些异常案例需要你亲自跟进？",
        "health": "今天哪怕只走10分钟也要走",
        "manage": "你自己的状态怎么样？诚实评估，1-10分打一个",
        "tonight": "今晚比平时早30分钟睡",
    },
    16: {
        "phase": "冲刺期",
        "work": "618还有2天，确认值班表已落实，每个时段有负责人",
        "health": "周末：补觉优先，工作消息设延迟回复",
        "manage": "今天告知团队：618当天遇到紧急情况的联系路径",
        "tonight": "今晚8小时睡眠，明天精力更好",
    },
    17: {
        "phase": "冲刺期",
        "work": "最后检查大促应急预案，重点：平台崩溃/舆情爆发/大规模投诉的处置路径",
        "health": "今天不做大量运动，保存体力",
        "manage": "给上级发一条简短的进度同步，让他知道你这边准备就绪",
        "tonight": "早睡，明天是大促前最后一个工作日",
    },
    18: {
        "phase": "冲刺期",
        "work": "618最后准备，确认所有系统正常，团队到位",
        "health": "今天吃好喝好，正餐不能省",
        "manage": "今天对团队说：'我们准备好了，遇到问题按SOP走，相信你们'",
        "tonight": "今晚可能会晚，但内心要平静，你们已经准备好了",
    },
    19: {
        "phase": "冲刺期",
        "work": "大促后D+1：盘点昨日投诉和问题，快速分类处理",
        "health": "大促高峰过了，今天喝一杯热茶，给自己一点喘息",
        "manage": "告诉团队：最难的部分过去了",
        "tonight": "今晚争取22:30之前到家",
    },
    20: {
        "phase": "冲刺期",
        "work": "处理大促遗留问题，非紧急的排到下周，不要全部今天压",
        "health": "今天做一次完整的午休",
        "manage": "识别大促期间团队表现出色的人，今天给他们发感谢",
        "tonight": "今晚22:00前到家",
    },
    21: {
        "phase": "冲刺期",
        "work": "大促数据复盘准备：收集核心指标，不急着出结论",
        "health": "今天走路30分钟，让身体缓过来",
        "manage": "大促后是团队凝聚的好时机，今天安排一顿团队聚餐或点心",
        "tonight": "21:30前到家",
    },
    22: {
        "phase": "冲刺期",
        "work": "继续处理大促遗留，重点关注S级商家整改进度",
        "health": "今天量一次体重和血压，了解真实健康状态",
        "manage": "今天一对一找一个团队成员聊：大促期间他们最难受的是什么",
        "tonight": "今晚不带电脑回家",
    },
    23: {
        "phase": "冲刺期",
        "work": "本周核心任务收尾，非紧急工作推到下周",
        "health": "睡眠目标重新提高到7小时",
        "manage": "今天花30分钟复盘：大促期间你自己的决策哪些是对的，哪些可以更好",
        "tonight": "21:00前到家（开始恢复正常节奏）",
    },
    24: {
        "phase": "冲刺期",
        "work": "大促复盘报告起草，重点：虚假品牌治理效果数据",
        "health": "今天做完整的锻炼（哪怕只是快走40分钟）",
        "manage": "和上级同步大促复盘，争取对你工作的正式反馈",
        "tonight": "今晚给自己奖励：做一件平时没时间做的事",
    },
    25: {
        "phase": "冲刺期",
        "work": "大促复盘：识别下次可以改进的3个流程",
        "health": "今天注意午饭质量，不吃外卖，换健康选项",
        "manage": "今天花10分钟读读你不熟悉的管理知识",
        "tonight": "21:00前到家",
    },
    26: {
        "phase": "冲刺期",
        "work": "整理大促期间积压的非紧急工作，按优先级排序",
        "health": "周末完全断开工作消息，充电",
        "manage": "今天不开会，留时间给自己深度思考",
        "tonight": "今晚好好休息",
    },
    27: {
        "phase": "冲刺期",
        "work": "周末：只处理真正紧急的事，其余等周一",
        "health": "今天睡到自然醒",
        "manage": "今天可以思考：你接手管理这8个月，什么地方成长了？",
        "tonight": "今晚做一件让自己开心的事",
    },

    # ══════════════════════════════
    # 第三阶段：大促后恢复期（Day 28-30，6/18+10天）
    # 核心：系统性恢复，建立可持续节奏
    # ══════════════════════════════
    28: {
        "phase": "恢复期",
        "work": "大促完整复盘报告完成，提交上级",
        "health": "今天安排一次正式体检预约（如果还没做的话）",
        "manage": "制定下个季度的团队工作节奏，避免下次大促重蹈覆辙",
        "tonight": "目标：今晚21:00到家，开始建立新常态",
    },
    29: {
        "phase": "恢复期",
        "work": "将大促经验固化为SOP，让下次大促不需要重新想一遍",
        "health": "开始规律运动计划：每周3次，每次30分钟，写进日历",
        "manage": "和团队开一个'大促总结会'：哪些做得好，哪些下次改",
        "tonight": "21:00前到家，这是新的正常",
    },
    30: {
        "phase": "恢复期",
        "work": "30天复盘：你的管理能力在哪里有了真实的进步？",
        "health": "30天健康数据回顾：睡眠、运动、压力各有什么变化？",
        "manage": "给自己写一封信：30天前的你需要听到什么？（留给未来的自己）",
        "tonight": "今晚好好庆祝：你撑过了第一次大促，这很了不起",
    },
}


def get_day_number(today: datetime.date = None) -> int:
    if today is None:
        today = datetime.date.today()
    delta = (today - START_DATE).days + 1
    return delta


def get_promotion_countdown(today: datetime.date = None) -> str:
    if today is None:
        today = datetime.date.today()
    delta = (PROMOTION_DATE - today).days
    if delta > 0:
        return f"距离618还有 {delta} 天"
    elif delta == 0:
        return "今天是618大促日！"
    else:
        return f"618大促已结束 {abs(delta)} 天"


def print_divider(char="─", width=60):
    print(char * width)


def show_today(today: datetime.date = None):
    if today is None:
        today = datetime.date.today()

    day_num = get_day_number(today)
    countdown = get_promotion_countdown(today)

    if day_num < 1 or day_num > 30:
        print(f"\n30天计划范围：{START_DATE} 至 {START_DATE + datetime.timedelta(days=29)}")
        print(f"今天是 {today}，不在计划范围内。")
        return

    plan = DAILY_PLAN.get(day_num)
    if not plan:
        print(f"Day {day_num} 暂无计划数据。")
        return

    print()
    print_divider("═")
    print(f"  Kenton，早上好！今天是计划第 {day_num} 天  [{plan['phase']}]")
    print(f"  {today.strftime('%Y年%m月%d日')}  |  {countdown}")
    print_divider("═")
    print()
    print(f"  【工作重点】{plan['work']}")
    print()
    print(f"  【健康提醒】{plan['health']}")
    print()
    print(f"  【管理功课】{plan['manage']}")
    print()
    print_divider()
    print(f"  今晚目标：{plan['tonight']}")
    print_divider()
    print()


def show_full_plan():
    print()
    print_divider("═")
    print("  Kenton 30天工作生活平衡规划总览")
    print(f"  起始：{START_DATE}  |  618大促：{PROMOTION_DATE}")
    print_divider("═")

    phases = {
        "预热期": ("05/22", "05/31", "Day 1-10",  "理清战场，建立底线"),
        "冲刺期": ("06/01", "06/20", "Day 11-27", "聚焦核心，保住底线，接受高强度"),
        "恢复期": ("06/21", "06/21", "Day 28-30", "系统性恢复，建立可持续节奏"),
    }

    for phase, (start, end, days, desc) in phases.items():
        print(f"\n  【{phase}】{days}（{start}~{end}）")
        print(f"  核心：{desc}")

    print()
    print("  每日提醒包含：工作重点 / 健康提醒 / 管理功课 / 今晚目标")
    print()
    print("  运行 `python3 kenton_30day_plan.py today` 查看今日计划")
    print("  运行 `python3 kenton_30day_plan.py <数字>` 查看指定第N天")
    print_divider("═")
    print()


def show_cron_setup():
    script_path = os.path.abspath(__file__)
    print()
    print_divider("═")
    print("  定时提醒设置方法（每天早上9:00自动提醒）")
    print_divider("═")
    print("""
  步骤1：打开 crontab 编辑器
  ─────────────────────────────
  $ crontab -e

  步骤2：添加以下一行（每天9:00执行）
  ─────────────────────────────""")
    print(f"  0 9 * * * python3 {script_path} today >> ~/kenton_reminder.log 2>&1")
    print("""
  步骤3：保存退出（vim 用 :wq，nano 用 Ctrl+O 再 Ctrl+X）

  步骤4：验证是否设置成功
  ─────────────────────────────
  $ crontab -l

  ─────────────────────────────
  其他时间选项：
    每天 8:30 提醒  →  30 8 * * *
    每天 9:00 提醒  →  0  9 * * *
    仅工作日提醒    →  0  9 * * 1-5

  日志查看：
  $ tail -20 ~/kenton_reminder.log
""")
    print_divider("═")
    print()


def main():
    args = sys.argv[1:]

    if not args or args[0] == "today":
        show_today()
    elif args[0] == "plan":
        show_full_plan()
    elif args[0] == "cron":
        show_cron_setup()
    else:
        try:
            day_num = int(args[0])
            target_date = START_DATE + datetime.timedelta(days=day_num - 1)
            show_today(target_date)
        except ValueError:
            print(f"\n用法：")
            print(f"  python3 kenton_30day_plan.py          # 今天的计划")
            print(f"  python3 kenton_30day_plan.py today    # 今天的计划")
            print(f"  python3 kenton_30day_plan.py plan     # 总览")
            print(f"  python3 kenton_30day_plan.py cron     # 定时设置方法")
            print(f"  python3 kenton_30day_plan.py <1-30>   # 指定第N天")


if __name__ == "__main__":
    main()
