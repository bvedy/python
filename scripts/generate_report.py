"""
京东假货舆情周报 - 自动生成脚本
每周三由 GitHub Actions 调用，使用 Claude API + web_search 搜集最新舆情并生成 HTML 报告
"""
import anthropic
import datetime
import os
import re


REPORT_PROMPT = """
你是京东合规假货治理部的资深分析师，兼顾平台合规视角与用户体验视角。
今天是 {today}。请通过 web_search 工具搜集**最近7天**的最新信息，生成一份深度京东假货舆情周报。

## 搜索任务（必须全部执行，共8次搜索）
1. "京东 假货 投诉 {year}年{month}月 最新"
2. "京东 商品质量 黑猫投诉 维权 {year}年{month}月"
3. "京东 全球购 贵金属 假冒 {year}年{month}月"
4. "电商平台 618 假货 大促 {year}年{month}月"
5. "拼多多 抖音 假货治理 {year}年{month}月 具体措施"
6. "淘宝 消费者保护 假货识别 {year}年{month}月"
7. "电商 假货 监管处罚 {year}年 最新"
8. "假货 用户投诉 消费体验 电商 {year}年{month}月"

## 报告结构（严格按此输出，内容要深度、具体）

### 第一章：风险趋势雷达
- 本周整体风险等级（高危/警示/平稳），与上周对比箭头
- 各品类风险热力：贵金属/奢侈品/化妆品/电子/食品 各自风险等级+环比变化
- 舆情声量走势：本周 vs 上周 vs 4周均值，用文字描述曲线趋势
- 早期预警信号（3～5个，提前识别下周可能爆发的风险点）

### 第二章：重点舆情事件深度拆解
每个事件（3～4个）必须包含以下5个层次：
① **事件概述**：what happened，来源，热度，日期
② **用户旅程还原**：从消费者视角，他在哪个环节被欺骗（发现→下单→收货→维权）
③ **平台漏洞下钻**：这个事件暴露了平台哪个具体环节的管控缺失（准入/在售/售后/处置）
④ **数据信号**：事件发生前，平台数据层面有哪些可捕捉的异常信号（评价异常/价格异常/退货率等）
⑤ **舆情风险传导路径**：此事件如何从个案演变为平台级信任危机

### 第三章：问题系统性下钻
选取本周最突出的2～3个系统性问题，每个问题做完整拆解：
- **问题定义**：一句话精确描述
- **根因树**：3层根因拆解（表象→直接原因→深层制度原因）
- **影响面**：涉及哪些品类、多少商家、消费者损失规模估算
- **现有治理的失效点**：当前措施为什么没解决这个问题

### 第四章：平台横向对比
淘宝/拼多多/抖音 vs 京东，按以下维度对比：
- 同类问题的发生率和处置速度
- 各平台在**用户体验侧**的差异化做法（消费者感知到的不同）
- 各平台在**合规机制侧**的差异（平台内部管控差异）
- 对京东的可借鉴点（明确标注★★★优先级）

### 第五章：治理打法与解决方案
每个方案必须同时覆盖两个视角：

**用户体验视角**（消费者能感知到什么变化）：
- 购前：风险提示、质量标签、价格对比如何呈现
- 购中：下单流程中的合规干预设计
- 购后：投诉体验优化、赔付流程简化

**平台合规视角**（平台内部机制如何设计）：
- 准入管控：商家资质、商品上架规则
- 在售监控：实时风险模型、抽检机制
- 处置闭环：违规响应、商家惩处、消费者赔付
- 制度建设：问责链条、数据基础设施

优先级分为：🔴P1立即行动 / 🟠P2本月完成 / 🟡P3本季度 / 🟢P4规划中

## HTML设计要求
- 配色主题：深蓝（#1a237e）为主色，风险等级用红/橙/黄/绿色标注
- 顶部：周报期数、监测周期、发布日期、本周总体风险等级（大字显示）
- 摘要栏：关键数字指标（事件数、高危品类数、投诉量、解决率）
- 每章有清晰的视觉层次：章标题→小节→正文
- 数据用表格，流程用有序步骤，对比用双列布局
- 适合部门负责人10分钟完整阅读
- 底部：内部参考文件，请勿对外传播

**只输出完整 HTML（从<!DOCTYPE html>到</html>），不要任何额外文字。**
"""


def get_week_number() -> int:
    return datetime.date.today().isocalendar()[1]


def generate_report() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = datetime.date.today()
    prompt = REPORT_PROMPT.format(
        today=today.strftime("%Y年%m月%d日"),
        year=today.year,
        month=today.month,
    )

    print(f"[{today}] 开始生成第 {get_week_number()} 周舆情报告...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": prompt}],
    )

    # 提取最终的 HTML 文本块
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    # 确保是完整 HTML
    if "<!DOCTYPE html>" not in html_content:
        raise ValueError("模型未返回完整 HTML，请检查 prompt 或 token 限制")

    # 只保留 HTML 部分（去掉前后可能存在的说明文字）
    match = re.search(r"(<!DOCTYPE html>.*</html>)", html_content, re.DOTALL | re.IGNORECASE)
    if match:
        html_content = match.group(1)

    return html_content


def save_report(html_content: str) -> str:
    today = datetime.date.today()
    filename = f"假货舆情周报_{today.strftime('%Y%m%d')}.html"
    output_path = os.path.join(os.path.dirname(__file__), "..", "reports", filename)
    output_path = os.path.normpath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"报告已保存：{output_path}")
    return output_path


if __name__ == "__main__":
    html = generate_report()
    path = save_report(html)
    print(f"完成：{path}")
