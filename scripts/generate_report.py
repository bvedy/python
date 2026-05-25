"""
京东假货舆情周报 - 自动生成脚本
每周三由 GitHub Actions 调用，使用 Claude API + web_search 搜集最新舆情并生成 HTML 报告
"""
import anthropic
import datetime
import os
import re


REPORT_PROMPT = """
你是京东合规假货治理部的专业分析师。今天是 {today}，大促期间。
请通过 web_search 工具搜集**最近7天**的最新信息，生成一份完整的京东假货舆情周报。

## 搜索要求
请依次搜索以下关键词（每个都要执行搜索）：
1. "京东 假货 投诉 {year}年{month}月"
2. "京东 商品质量 维权 舆情 {year}年{month}月"
3. "拼多多 抖音 淘宝 假货治理 {year}年{month}月"
4. "电商平台 假货 监管 {year}年{month}月"

## 报告要求
基于搜索结果，输出一份**完整的 HTML 文件内容**（从 <!DOCTYPE html> 到 </html>），包含：

1. **本周重点舆情事件**（2～4个，注明热度等级 高/中/低、事件来源、日期）
2. **假货问题趋势分析**（上升/下降趋势，结构性根因）
3. **其他平台对比**（淘宝/拼多多/抖音，各自现状和举措，对京东的借鉴价值）
4. **本周治理建议**（P1-P4 优先级排序，具体可执行）
5. **信息来源列表**（带 URL 的超链接）

## 设计要求
- 配色主题：深蓝色（#1a237e）为主色
- 顶部显示：周报期数、监测周期（本周一至今日）、发布日期
- 顶部摘要栏：本周重点事件数、高热度事件数、高发场景、趋势方向
- 内容专业、简洁，适合部门负责人快速阅读
- 底部注明：内部参考文件，请勿对外传播

**只输出 HTML 内容本身，不要有任何额外说明文字。**
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
