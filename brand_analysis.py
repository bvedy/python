#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品牌真伪和价格风险分析脚本
核心问题：
1. 是否假洋牌 (fake foreign brand)
2. 价格是否虚高 (price inflation risk)
"""

import openpyxl
from collections import defaultdict
import re

# 全球真实品牌数据库（按品类）
REAL_BRANDS_DB = {
    'Beauty': {
        'MAC', 'Estee Lauder', 'Clinique', 'Bobbi Brown', 'Origins',
        'L\'Oreal', 'Lancome', 'Maybelline', 'Garnier', 'Vichy',
        'La Roche-Posay', 'Kiehl\'s', 'Shiseido', 'SK-II', 'Anessa',
        'Biore', 'Hada Labo', 'Neutrogena', 'Olay', 'Dove',
        'Nivea', 'Vaseline', 'Johnson & Johnson', 'Cetaphil', 'CeraVe',
        'Bioderma', 'Eucerin', 'Cetyl', 'Avene', 'Uriage',
        'Clarins', 'Caudalie', 'NARS', 'Urban Decay', 'Naked',
        'Stila', 'Too Faced', 'Benefit', 'Smashbox', 'Tarte',
        'Charlotte Tilbury', 'Givenchy Beauty', 'YSL', 'Chanel', 'Dior',
        'Fenty Beauty', 'MAC Fix+', 'Morphe', 'Kylie Cosmetics', 'Hailey'
    },
    'Skincare': {
        'SK-II', 'La Mer', 'Estee Lauder', 'Origins', 'Clinique',
        'Kiehl\'s', 'Cetaphil', 'CeraVe', 'Olay', 'Dove',
        'Nivea', 'Bioderma', 'Eucerin', 'La Roche-Posay', 'Vichy',
        'Shiseido', 'Hada Labo', 'Biore', 'Muji', 'Rohto',
        'Caudalie', 'Clarins', 'Sisley', 'Lancome', 'Dior',
        'Chanel', 'Givenchy', 'Guerlain'
    },
    'Fragrance': {
        'Chanel', 'Dior', 'Guerlain', 'Givenchy', 'YSL',
        'Lancome', 'Estee Lauder', 'Clinique', 'Calvin Klein', 'Prada',
        'Armani', 'Dolce Gabbana', 'Tom Ford', 'Marc Jacobs', 'Coach',
        'Burberry', 'Versace', 'Hermes', 'Celine', 'Fendi'
    },
    'Apparel': {
        'Nike', 'Adidas', 'Puma', 'Reebok', 'New Balance',
        'Converse', 'Vans', 'Under Armour', 'Lululemon', 'Gymshark',
        'Zara', 'H&M', 'Uniqlo', 'Gap', 'Forever 21',
        'ASOS', 'Topshop', 'River Island', 'Boohoo', 'PrettyLittleThing',
        'Shein', 'Fashion Nova', 'PLT', 'Missguided', 'Prettylittlething'
    },
    'Food & Beverage': {
        'Nestle', 'Coca-Cola', 'PepsiCo', 'Kraft Heinz', 'General Mills',
        'Mondelez', 'Ferrero', 'Mars', 'Hershey', 'Lindt',
        'Godiva', 'Haagen-Dazs', 'Ben & Jerry', 'Starbucks', 'Nescafe',
        'Nespresso', 'Dolce Gusto', 'Lipton', 'Twinings', 'Haribo',
        'Mentos', 'Skittles', 'M&M', 'Oreo', 'Cadbury'
    },
    'Health & Wellness': {
        'Omron', 'Beurer', 'Braun', 'Oral-B', 'Philips',
        'Panasonic', 'Remington', 'Dyson', 'Apple Watch', 'Fitbit',
        'Garmin', 'GoPro', 'Canon', 'Nikon', 'Sony'
    },
    'Home & Kitchen': {
        'Dyson', 'KitchenAid', 'Instant Pot', 'Ninja', 'Vitamix',
        'Vitamix', 'Blendtec', 'OXO', 'Le Creuset', 'Staub',
        'All-Clad', 'Calphalon', 'T-Fal', 'Farberware', 'Cuisinart',
        'Oster', 'Sunbeam', 'Hamilton Beach', 'Delonghi', 'Saeco'
    }
}

# 平铺所有真实品牌集合
ALL_REAL_BRANDS = set()
for brands_in_category in REAL_BRANDS_DB.values():
    ALL_REAL_BRANDS.update(brands_in_category)

# 已知的假品牌黑名单（根据历史案例）
KNOWN_FAKE_BRANDS = {
    '雅诗陆兰', '兰蔻美', '兰蔻思', '雪花秀美',
    '欧莱雅美', '香奈儿美', '迪奥美', '圣罗兰美',
    '爱马仕美', '芬迪美', '范思哲美', '普拉达美'
}

def is_real_brand(brand_name):
    """判断是否是真实品牌"""
    if not isinstance(brand_name, str):
        brand_name = str(brand_name).strip()

    brand_name = brand_name.strip()
    if not brand_name:
        return False, 'empty'

    # 检查已知黑名单
    if brand_name in KNOWN_FAKE_BRANDS:
        return False, 'blacklist'

    # 检查真实品牌数据库
    if brand_name in ALL_REAL_BRANDS:
        return True, 'confirmed'

    # 检查品牌名称中是否包含真实品牌
    for real_brand in ALL_REAL_BRANDS:
        if real_brand.lower() in brand_name.lower():
            return True, 'contains_real_brand'

    return False, 'unknown'


def detect_fake_brand_patterns(brand_name):
    """检测假洋牌特征"""
    if not isinstance(brand_name, str):
        brand_name = str(brand_name).strip()

    brand_name = brand_name.strip()
    signals = []
    confidence = 0

    # 特征1：中文前缀 + 外文（典型假洋牌特征）
    has_chinese = bool(re.search(r'[一-鿿]', brand_name))
    has_english = bool(re.search(r'[a-zA-Z]', brand_name))

    if has_chinese and has_english:
        signals.append('中英混合')
        confidence += 40
    elif has_chinese:
        signals.append('纯中文品牌')
        confidence += 20

    # 特征2：多品牌组合（如"Dr.Forster,RHYMBA HILLS"）
    if ',' in brand_name or '、' in brand_name or '/' in brand_name:
        signals.append('多品牌组合')
        confidence += 35

    # 特征3：不符合品牌命名规律的字母组合
    if re.search(r'[aeiou]', brand_name.lower()):
        vowel_count = len(re.findall(r'[aeiou]', brand_name.lower()))
        word_length = len(brand_name)
        if word_length > 8 and vowel_count < word_length * 0.2:
            signals.append('元音稀少')
            confidence += 25

    # 特征4：特殊字符过多
    special_chars = len(re.findall(r'[^a-zA-Z0-9一-鿿\s]', brand_name))
    if special_chars > 2:
        signals.append('特殊字符过多')
        confidence += 20

    # 特征5：品牌名称过长（超过30字符可能是描述而非品牌）
    if len(brand_name) > 30:
        signals.append('名称过长')
        confidence += 15

    # 特征6：数字前缀或后缀（如"365品牌"）
    if re.search(r'^\d+', brand_name) or re.search(r'\d+$', brand_name):
        signals.append('数字前后缀')
        confidence += 25

    return signals, min(confidence, 100)


def assess_price_risk(brand_name):
    """评估价格虚高风险

    注意：没有实际价格数据，只能基于品牌特征推断风险
    """
    signals = []
    risk_level = 'low'  # low, medium, high
    confidence = 'low'

    is_real, reason = is_real_brand(brand_name)

    if not is_real:
        # 非真实品牌的假货通常定价虚高
        signals.append('非真实品牌通常价格虚高')
        risk_level = 'high'
        confidence = 'medium'
    else:
        # 真实品牌的价格虚高风险较低
        signals.append('真实品牌价格相对透明')
        risk_level = 'low'
        confidence = 'high'

    # 品牌名过长可能隐含虚高
    if len(brand_name) > 30:
        signals.append('品牌名过长，可能含虚假宣传')
        if risk_level == 'low':
            risk_level = 'medium'

    return risk_level, signals, confidence


def analyze_brand(brand_name):
    """完整分析一个品牌"""
    if not isinstance(brand_name, str):
        brand_name = str(brand_name).strip()

    brand_name = brand_name.strip()

    # 1. 检查是否真实品牌
    is_real, real_reason = is_real_brand(brand_name)

    # 2. 检测假洋牌特征
    fake_signals, fake_confidence = detect_fake_brand_patterns(brand_name)

    # 3. 评估价格虚高风险
    price_risk, price_signals, price_confidence = assess_price_risk(brand_name)

    # 判断最终结论
    is_fake_foreign = 'no' if is_real else 'yes'

    # 置信度评级
    if fake_confidence >= 75:
        confidence_level = 'high'
    elif fake_confidence >= 45:
        confidence_level = 'medium'
    else:
        confidence_level = 'low'

    return {
        'brand': brand_name,
        'is_fake_foreign': is_fake_foreign,
        'fake_confidence': fake_confidence,
        'fake_signals': fake_signals,
        'price_risk': price_risk,
        'price_signals': price_signals,
        'is_real_brand': is_real,
        'real_reason': real_reason,
        'confidence_level': confidence_level,
        'risk_score': fake_confidence if is_fake_foreign == 'yes' else 0
    }


def main():
    # 从Excel读取品牌列表
    excel_path = None

    # 查找Excel文件
    import os
    import glob

    # 在当前目录查找
    excel_files = glob.glob('/home/user/python/**/*.xlsx', recursive=True)
    if not excel_files:
        excel_files = glob.glob('*.xlsx')

    if excel_files:
        excel_path = excel_files[0]
        print(f"找到文件: {excel_path}")
    else:
        print("未找到Excel文件，请将包含品牌列表的Excel文件放入当前目录")
        print("脚本已准备就绪，等待数据文件...")
        return

    # 读取Excel
    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        ws = wb.active

        brands = []
        for row in ws.iter_rows(min_row=1, max_col=1, values_only=True):
            if row[0]:
                brand_name = str(row[0]).strip()
                if brand_name and brand_name.lower() != 'brand':
                    brands.append(brand_name)

        print(f"加载了 {len(brands)} 个品牌")

        # 分析所有品牌
        results = []
        for brand in brands:
            result = analyze_brand(brand)
            results.append(result)

        # 按风险排序
        results.sort(key=lambda x: (x['is_fake_foreign'] == 'yes', -x['fake_confidence']),
                     reverse=True)

        # 输出结果
        output = []
        output.append("=" * 120)
        output.append("品牌真伪与价格风险分析报告")
        output.append("=" * 120)
        output.append("")

        # 统计信息
        fake_count = sum(1 for r in results if r['is_fake_foreign'] == 'yes')
        high_price_risk = sum(1 for r in results if r['price_risk'] == 'high')

        output.append(f"总品牌数: {len(results)}")
        output.append(f"假洋牌检测: {fake_count} 个 ({fake_count*100/len(results):.1f}%)")
        output.append(f"高价格虚高风险: {high_price_risk} 个 ({high_price_risk*100/len(results):.1f}%)")
        output.append("")
        output.append("-" * 120)
        output.append("")

        # 详细结果
        for i, result in enumerate(results[:50], 1):  # 显示前50个（最高风险）
            output.append(f"{i}. 品牌: {result['brand']}")
            output.append(f"   假洋牌: {result['is_fake_foreign']} (置信度: {result['fake_confidence']}%, {result['confidence_level']})")

            if result['fake_signals']:
                output.append(f"   假洋牌特征: {', '.join(result['fake_signals'])}")

            output.append(f"   价格虚高风险: {result['price_risk']}")
            if result['price_signals']:
                output.append(f"   原因: {', '.join(result['price_signals'])}")

            output.append("")

        # 保存完整结果到文件
        output_text = "\n".join(output)

        with open('/tmp/brand_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(output_text)

        print(output_text)
        print(f"\n完整报告已保存到 /tmp/brand_analysis_report.txt")

        # 也保存为CSV格式便于后续处理
        with open('/tmp/brand_analysis_results.csv', 'w', encoding='utf-8') as f:
            f.write("品牌,假洋牌,假洋牌置信度,假洋牌特征,价格虚高风险,原因\n")
            for result in results:
                signals_str = '|'.join(result['fake_signals']) if result['fake_signals'] else ''
                price_reasons = '|'.join(result['price_signals']) if result['price_signals'] else ''
                f.write(f'"{result["brand"]}",{result["is_fake_foreign"]},{result["fake_confidence"]},"{signals_str}",{result["price_risk"]},"{price_reasons}"\n')

        print(f"CSV格式已保存到 /tmp/brand_analysis_results.csv")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
