#!/usr/bin/env python3
"""工作生活平衡管理系统 - 专为新晋管理者设计"""

import json
import os
import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path


DATA_FILE = Path.home() / ".work_life_balance.json"


@dataclass
class DailyRecord:
    date: str
    work_start: str
    work_end: str
    stress_level: int        # 1-10
    sleep_hours: float
    exercise_done: bool
    mood: int                # 1-10
    notes: str = ""

    @property
    def work_hours(self) -> float:
        start = datetime.datetime.strptime(self.work_start, "%H:%M")
        end = datetime.datetime.strptime(self.work_end, "%H:%M")
        delta = end - start
        if delta.total_seconds() < 0:
            delta += datetime.timedelta(days=1)
        return delta.total_seconds() / 3600

    @property
    def overtime_hours(self) -> float:
        return max(0, self.work_hours - 8)


class WorkLifeBalanceManager:
    def __init__(self):
        self.records: list[dict] = []
        self.load_data()

    def load_data(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def add_record(self, record: DailyRecord):
        self.records.append(asdict(record))
        self.save_data()

    def get_weekly_stats(self) -> dict:
        if not self.records:
            return {}
        cutoff = datetime.date.today() - datetime.timedelta(days=7)
        weekly = [
            r for r in self.records
            if datetime.date.fromisoformat(r["date"]) >= cutoff
        ]
        if not weekly:
            return {}
        records = [DailyRecord(**r) for r in weekly]
        avg_work_hours = sum(r.work_hours for r in records) / len(records)
        avg_stress = sum(r.stress_level for r in records) / len(records)
        avg_sleep = sum(r.sleep_hours for r in records) / len(records)
        avg_mood = sum(r.mood for r in records) / len(records)
        exercise_days = sum(1 for r in records if r.exercise_done)
        return {
            "days_recorded": len(records),
            "avg_work_hours": round(avg_work_hours, 1),
            "avg_stress": round(avg_stress, 1),
            "avg_sleep": round(avg_sleep, 1),
            "avg_mood": round(avg_mood, 1),
            "exercise_days": exercise_days,
        }


def get_health_assessment(stats: dict) -> tuple[str, list[str]]:
    """根据数据评估健康风险级别，返回(级别, 建议列表)"""
    if not stats:
        return "未知", ["请先记录至少一天的数据"]

    risk_score = 0
    advice = []

    work_hours = stats["avg_work_hours"]
    if work_hours >= 13:
        risk_score += 3
        advice.append(f"每天平均{work_hours}小时工作严重超标，必须立即减少加班")
    elif work_hours >= 10:
        risk_score += 2
        advice.append(f"每天平均{work_hours}小时工作超标，建议设定每天下班时间红线")
    elif work_hours >= 9:
        risk_score += 1
        advice.append("工作时间略超，尽量控制在9小时内")

    stress = stats["avg_stress"]
    if stress >= 8:
        risk_score += 3
        advice.append("压力极高，强烈建议寻求专业心理咨询或向上级反馈")
    elif stress >= 6:
        risk_score += 2
        advice.append("压力偏高，需要主动寻找减压方法")
    elif stress >= 4:
        risk_score += 1
        advice.append("压力中等，注意定期释放压力")

    sleep = stats["avg_sleep"]
    if sleep < 5:
        risk_score += 3
        advice.append(f"平均睡眠{sleep}小时严重不足，长期如此会损伤认知功能")
    elif sleep < 6.5:
        risk_score += 2
        advice.append(f"平均睡眠{sleep}小时不足，建议每天争取7小时以上")
    elif sleep < 7:
        risk_score += 1
        advice.append("睡眠稍不足，尽量保证7小时")

    if stats["exercise_days"] == 0:
        risk_score += 2
        advice.append("本周完全没有运动，每天哪怕步行20分钟也有帮助")
    elif stats["exercise_days"] <= 2:
        risk_score += 1
        advice.append("本周运动偏少，建议每周至少3天运动")

    if risk_score >= 8:
        level = "高危"
    elif risk_score >= 5:
        level = "警戒"
    elif risk_score >= 3:
        level = "需关注"
    else:
        level = "良好"

    return level, advice


MANAGEMENT_TIPS = [
    {
        "category": "时间管理",
        "tip": "用'艾森豪威尔矩阵'分类任务：紧急+重要立刻做，重要不紧急计划做，紧急不重要委派，都不是就删除",
        "action": "今天整理一份任务清单，按此矩阵分类，找出哪些事可以授权给团队"
    },
    {
        "category": "向上管理",
        "tip": "新晋管理者最常见误区：什么都自己扛。与你的上级对齐期望值，明确哪些决策你可以自主，哪些需汇报",
        "action": "本周安排一次与上级的1:1会议，梳理你的职责边界"
    },
    {
        "category": "团队授权",
        "tip": "做管理者不是'做最多的那个人'，而是'让团队产出最大'。每周问自己：哪些事情只有我能做？其他的都应该授权",
        "action": "列出你本周做的所有事，圈出哪些团队成员可以接手"
    },
    {
        "category": "心理韧性",
        "tip": "新管理者的'冒充者综合症'很普遍——感觉自己能力不够不代表你真的不够，代表你在认真思考",
        "action": "每天写下3件自己做得好的小事，建立正向自我认知"
    },
    {
        "category": "健康优先",
        "tip": "管理者的核心资产是精力和判断力，这两者都依赖身体健康。你的健康垮了，团队才真正没有依靠",
        "action": "今天设定一个硬性下班时间（如21:00），作为不可侵犯的边界"
    },
    {
        "category": "沟通效率",
        "tip": "减少无效会议：每个会议必须有明确目标和结论，没有目标的会议改为异步文档沟通",
        "action": "审查本周的会议，取消或合并那些没有清晰目标的会议"
    },
    {
        "category": "寻求支持",
        "tip": "找一位有经验的管理者作为非正式导师，他们走过的坑可以让你少踩很多",
        "action": "思考你认识的管理者中，谁是你可以请教的对象，本周联系一位"
    },
]


def show_daily_tip():
    day_of_year = datetime.date.today().timetuple().tm_yday
    tip = MANAGEMENT_TIPS[day_of_year % len(MANAGEMENT_TIPS)]
    print("\n" + "="*60)
    print(f"  今日管理建议【{tip['category']}】")
    print("="*60)
    print(f"  {tip['tip']}")
    print(f"\n  行动项：{tip['action']}")
    print("="*60)


def log_today(manager: WorkLifeBalanceManager):
    print("\n--- 记录今天的工作生活数据 ---")
    today = datetime.date.today().isoformat()

    existing = [r for r in manager.records if r["date"] == today]
    if existing:
        print(f"今天({today})已有记录。是否覆盖？(y/n): ", end="")
        if input().strip().lower() != "y":
            return

    try:
        work_start = input("上班时间 (如 09:00): ").strip() or "09:00"
        work_end = input("下班到家时间 (如 22:00): ").strip() or "22:00"
        stress_level = int(input("今日压力(1-10，10最高): ").strip())
        sleep_hours = float(input("昨晚睡眠小时数: ").strip())
        exercise_input = input("今天有运动吗？(y/n): ").strip().lower()
        exercise_done = exercise_input == "y"
        mood = int(input("今日心情(1-10，10最好): ").strip())
        notes = input("备注（可选，直接回车跳过）: ").strip()

        record = DailyRecord(
            date=today,
            work_start=work_start,
            work_end=work_end,
            stress_level=max(1, min(10, stress_level)),
            sleep_hours=max(0, min(24, sleep_hours)),
            exercise_done=exercise_done,
            mood=max(1, min(10, mood)),
            notes=notes,
        )

        manager.add_record(record)

        print(f"\n已记录！今日工作时长：{record.work_hours:.1f}小时，加班：{record.overtime_hours:.1f}小时")
        if record.work_hours >= 12:
            print("  警告：今日工作超过12小时，请确保充分休息！")
    except (ValueError, KeyboardInterrupt):
        print("\n记录取消。")


def show_report(manager: WorkLifeBalanceManager):
    stats = manager.get_weekly_stats()
    if not stats:
        print("\n暂无数据。请先记录至少一天的数据。")
        return

    level, advice = get_health_assessment(stats)

    print("\n" + "="*60)
    print("  本周工作生活平衡报告")
    print("="*60)
    print(f"  记录天数：    {stats['days_recorded']} 天")
    print(f"  平均工作时间：{stats['avg_work_hours']} 小时/天")
    print(f"  平均压力指数：{stats['avg_stress']} / 10")
    print(f"  平均睡眠时间：{stats['avg_sleep']} 小时/天")
    print(f"  平均心情指数：{stats['avg_mood']} / 10")
    print(f"  本周运动天数：{stats['exercise_days']} 天")
    print(f"\n  健康风险评估：【{level}】")
    print("="*60)

    if advice:
        print("\n  改善建议：")
        for i, a in enumerate(advice, 1):
            print(f"  {i}. {a}")

    if stats["avg_work_hours"] >= 12:
        print("\n  重要提示：您目前每天工作超过12小时。")
        print("  长期高强度工作会导致：判断力下降、创造力减弱、")
        print("  免疫力降低，以及更高的心血管疾病风险。")
        print("  这不是靠'努力'就能克服的生理规律，请认真对待。")


def show_emergency_advice():
    """针对当前用户情况的针对性建议"""
    print("\n" + "="*60)
    print("  针对您当前情况的专项建议")
    print("="*60)
    print("""
  您的情况：35岁，每天9:00-22:00（13小时），新晋管理者，
  压力大、能力焦虑、健康下滑。

  【最重要的三件事】

  1. 身体是底线，不是筹码
     - 立刻安排一次全面体检，了解真实健康状况
     - 每周至少3次、每次30分钟的中等强度运动
       （快走也算）
     - 睡眠不能少于6.5小时，这是认知功能的底线

  2. 13小时工作日是系统问题，不是努力程度问题
     - 记录一周你的时间：哪些会议可以取消？
       哪些工作可以授权？哪些是真正只有你能做的？
     - 设定"最晚20:30离开办公室"为红线，
       剩下的事明天再说
     - 长时间工作的边际产出接近零，质量比数量重要

  3. 新管理者的能力焦虑是正常的，但需要主动应对
     - 接手管理才7个月，焦虑正常，不代表你不行
     - 找一位愿意指导你的前辈管理者
     - 考虑管理类课程或书籍（推荐：《成为技术领导者》
       《高效能人士的七个习惯》）

  【今天就能做的一件事】
  和你的上级约一次谈话，坦诚说出你面临的挑战，
  明确你需要的支持。这不是软弱，而是成熟的管理者行为。
""")
    print("="*60)


def main():
    manager = WorkLifeBalanceManager()

    print("\n" + "="*60)
    print("     工作生活平衡管理系统")
    print("     专为新晋管理者设计")
    print("="*60)

    while True:
        print("\n请选择：")
        print("  1. 记录今日数据")
        print("  2. 查看本周报告")
        print("  3. 查看今日管理建议")
        print("  4. 查看针对您情况的专项建议")
        print("  0. 退出")
        print("\n选择 (0-4): ", end="")

        choice = input().strip()

        if choice == "1":
            log_today(manager)
        elif choice == "2":
            show_report(manager)
        elif choice == "3":
            show_daily_tip()
        elif choice == "4":
            show_emergency_advice()
        elif choice == "0":
            print("\n记得照顾好自己。再见！\n")
            break
        else:
            print("无效选择，请重新输入。")


if __name__ == "__main__":
    main()
