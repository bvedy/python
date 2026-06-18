#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品牌最终分类脚本：
1. 分析已验证的110个品牌的规律
2. 对剩余2496个品牌进行智能规则分类
3. 生成最终报告
"""

import csv
import re
from collections import defaultdict

# 读取已验证的品牌
verified = {}
with open('/home/user/python/核验/核验结果.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        verified[row['品牌']] = {
            'judgment': row['判定'],
            'country': row['宣称国'],
            'reason': row['理由'],
            'strength': row['证据强度']
        }

# 读取品牌清单
brands_list = []
with open('/home/user/python/核验/品牌清单.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        brands_list.append((row['序号'], row['品牌']))

# 分析已验证品牌的规律
def analyze_patterns():
    """从已验证的110个品牌提取规律"""
    patterns = {
        'true_foreign': [],
        'fake_brands': [],
        'suspicious': [],
        'uncertain': [],
        'domestic': [],
        'multi_brand': []
    }

    for brand_name, info in verified.items():
        judgment = info['judgment']
        if judgment == '真洋牌' or '真洋牌' in judgment:
            patterns['true_foreign'].append(brand_name)
        elif judgment == '假洋牌':  # 确认假洋牌，不含疑似
            patterns['fake_brands'].append(brand_name)
        elif judgment == '疑似假洋牌':  # 疑似假洋牌
            patterns['suspicious'].append(brand_name)
        elif '存疑' in judgment:
            patterns['uncertain'].append(brand_name)
        elif '国产' in judgment or '非假洋牌' in judgment:
            patterns['domestic'].append(brand_name)
        elif '多品牌' in judgment:
            patterns['multi_brand'].append(brand_name)

    return patterns

def classify_brand(brand_name):
    """对未验证的品牌进行分类"""

    # 检查是否多品牌组合
    if ',' in brand_name or '/' in brand_name:
        return '待核验(多品牌组合)', '规则推断·未核验'

    # 检查是否纯中文
    chinese_chars = len(re.findall(r'[一-鿿]', brand_name))
    english_chars = len(re.findall(r'[a-zA-Z]', brand_name))
    numbers = len(re.findall(r'[0-9]', brand_name))

    total_content = chinese_chars + english_chars + numbers

    # 纯中文品牌 → 非假洋牌
    if english_chars == 0 and numbers == 0 and chinese_chars > 0:
        return '非假洋牌(国产)', '规则推断·未核验'

    # 纯英文/纯数字 + 长度短 (3-4字母) → 可能是真洋牌或难以判断
    if english_chars > 0 and chinese_chars == 0:
        # 检查生造特征：缺少元音
        vowels = len(re.findall(r'[aeiouAEIOU]', brand_name))
        if total_content > 0 and vowels == 0:
            return '疑似假洋牌(无元音)', '规则推断·未核验'
        if total_content > 0 and vowels / total_content < 0.15:
            return '疑似假洋牌(元音<15%)', '规则推断·未核验'
        # 正常英文名
        return '待核验(英文名)', '规则推断·未核验'

    # 中英混合
    if chinese_chars > 0 and english_chars > 0:
        return '待核验(中英混合)', '规则推断·未核验'

    return '待核验(未分类)', '规则推断·未核验'

# 生成最终判定表
def generate_final_table():
    """生成全量品牌判定表"""

    results = [['序号', '品牌', '判定', '价格虚高风险', '原因', '数据来源']]

    verified_count = 0
    rule_inferred_count = 0

    for seq, brand_name in brands_list:
        if brand_name in verified:
            # 已验证的品牌
            info = verified[brand_name]
            judgment = info['judgment']

            # 判断价格虚高风险
            if judgment == '假洋牌':  # 确认假洋牌
                price_risk = '极高'
            elif judgment == '疑似假洋牌':  # 疑似假洋牌
                price_risk = '高'
            elif '真洋牌' in judgment:
                price_risk = '低-中'
            elif '存疑' in judgment:
                price_risk = '低'
            elif '国产' in judgment or '非假洋牌' in judgment:
                price_risk = '极低'
            else:
                price_risk = '未知'

            results.append([
                seq,
                brand_name,
                judgment,
                price_risk,
                info['reason'][:100] if info['reason'] else '',  # 截断理由
                '已联网核验'
            ])
            verified_count += 1
        else:
            # 规则推断
            judgment, source = classify_brand(brand_name)

            # 判断价格虚高风险
            if '疑似假洋牌' in judgment:
                price_risk = '高'
            elif '非假洋牌' in judgment:
                price_risk = '低'
            elif '待核验' in judgment:
                price_risk = '待核验'
            else:
                price_risk = '未知'

            # 判定原因
            if '多品牌' in judgment:
                reason = '多品牌拼接,需拆分核实'
            elif '纯中文' in judgment:
                reason = '纯中文品牌,不属假洋牌'
            elif '无元音' in judgment:
                reason = '无元音字母,高风险生造名'
            elif '元音<15%' in judgment:
                reason = '元音占比低,疑似生造名'
            elif '中英混合' in judgment:
                reason = '中英混合,通常为真品牌,需逐个搜索'
            elif '英文名' in judgment:
                reason = '英文名,需联网核验'
            else:
                reason = '需进一步核实'

            results.append([
                seq,
                brand_name,
                judgment,
                price_risk,
                reason,
                source
            ])
            rule_inferred_count += 1

    # 保存到文件
    with open('/home/user/python/核验/全量品牌最终判定表.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)

    return verified_count, rule_inferred_count

if __name__ == '__main__':
    patterns = analyze_patterns()
    verified_count, rule_count = generate_final_table()

    print(f"=== 分类统计 ===")
    print(f"已联网核验: {verified_count}")
    print(f"规则推断: {rule_count}")
    print(f"总计: {verified_count + rule_count}")

    print(f"\n=== 已验证品牌分布 ===")
    print(f"真洋牌: {len(patterns['true_foreign'])}")
    print(f"确认假洋牌: {len(patterns['fake_brands'])}")
    print(f"疑似假洋牌: {len(patterns['suspicious'])}")
    print(f"存疑: {len(patterns['uncertain'])}")
    print(f"国产: {len(patterns['domestic'])}")
    print(f"多品牌: {len(patterns['multi_brand'])}")

    print("\n✅ 全量判定表已生成: /home/user/python/核验/全量品牌最终判定表.csv")
