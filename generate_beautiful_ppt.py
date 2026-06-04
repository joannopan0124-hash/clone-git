#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI英语学习助手 - 美观PPT生成脚本
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 创建演示文稿
prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9 比例
prs.slide_height = Inches(7.5)

def add_gradient_background(slide, color1, color2):
    """添加渐变背景"""
    # 顶部渐变
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color1
    shape.line.fill.background()
    
    # 底部渐变条
    bottom_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(6.5),
        prs.slide_width, Inches(1)
    )
    bottom_shape.fill.solid()
    bottom_shape.fill.fore_color.rgb = color2
    bottom_shape.line.fill.background()

def add_decorative_circles(slide):
    """添加装饰性圆点"""
    colors = [
        RGBColor(59, 130, 246),
        RGBColor(168, 85, 247),
        RGBColor(251, 146, 60),
        RGBColor(34, 197, 94),
    ]
    
    positions = [
        (0.3, 0.3), (11.5, 0.5), (0.2, 6.2), (11.8, 6.0),
    ]
    
    for i, (x, y) in enumerate(positions):
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x), Inches(y),
            Inches(0.8), Inches(0.8)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = colors[i % len(colors)]
        circle.line.fill.background()
        circle.fill.transparency = 0.5

def add_title_slide(prs, title, subtitle):
    """添加标题幻灯片"""
    slide_layout = prs.slide_layouts[6]  # 空白布局
    slide = prs.slides.add_slide(slide_layout)
    
    # 添加背景
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = RGBColor(248, 250, 252)
    bg_shape.line.fill.background()
    
    # 添加装饰元素
    add_decorative_circles(slide)
    
    # 左侧装饰块
    left_deco = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        Inches(0.3), prs.slide_height
    )
    left_deco.fill.solid()
    left_deco.fill.fore_color.rgb = RGBColor(59, 130, 246)
    left_deco.line.fill.background()
    
    # 标题主色块
    title_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1.5), Inches(2),
        Inches(10), Inches(3.5)
    )
    title_bg.fill.solid()
    title_bg.fill.fore_color.rgb = RGBColor(59, 130, 246)
    title_bg.line.fill.background()
    
    # 添加标题
    title_box = slide.shapes.add_textbox(
        Inches(2), Inches(2.5),
        Inches(9), Inches(1.5)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(56)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 添加副标题
    subtitle_box = slide.shapes.add_textbox(
        Inches(1.5), Inches(4.3),
        Inches(10), Inches(1)
    )
    tf = subtitle_box.text_frame
    tf.paragraphs[0].text = subtitle
    tf.paragraphs[0].font.size = Pt(28)
    tf.paragraphs[0].font.color.rgb = RGBColor(71, 85, 105)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    return slide

def add_feature_card(slide, x, y, title, description, color, icon_text=None):
    """添加功能卡片"""
    # 卡片背景
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y),
        Inches(3.8), Inches(2.2)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = color
    card.line.fill.background()
    
    # 添加阴影效果
    card.shadow.inherit = False
    
    # 标题
    title_box = slide.shapes.add_textbox(
        Inches(x + 0.2), Inches(y + 0.2),
        Inches(3.4), Inches(0.5)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    # 描述
    desc_box = slide.shapes.add_textbox(
        Inches(x + 0.2), Inches(y + 0.7),
        Inches(3.4), Inches(1.3)
    )
    tf = desc_box.text_frame
    tf.paragraphs[0].text = description
    tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    tf.word_wrap = True
    
    if icon_text:
        icon_box = slide.shapes.add_textbox(
            Inches(x + 3.0), Inches(y + 0.1),
            Inches(0.5), Inches(0.5)
        )
        tf = icon_box.text_frame
        tf.paragraphs[0].text = icon_text
        tf.paragraphs[0].font.size = Pt(20)

def add_content_slide(prs, title, content_list, colors=None):
    """添加内容幻灯片"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # 背景
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = RGBColor(248, 250, 252)
    bg_shape.line.fill.background()
    
    add_decorative_circles(slide)
    
    # 标题栏
    title_bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    title_bar.fill.solid()
    title_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
    title_bar.line.fill.background()
    
    title_box = slide.shapes.add_textbox(
        Inches(0.7), Inches(0.4),
        Inches(11.6), Inches(0.6)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    # 添加内容
    y_positions = [1.5, 1.5, 1.5, 4.0, 4.0, 4.0]
    x_positions = [0.7, 4.8, 8.9, 0.7, 4.8, 8.9]
    
    default_colors = [
        RGBColor(59, 130, 246),
        RGBColor(168, 85, 247),
        RGBColor(251, 146, 60),
        RGBColor(34, 197, 94),
        RGBColor(236, 72, 153),
        RGBColor(99, 102, 241),
    ]
    
    for i, (item_title, item_desc) in enumerate(content_list):
        color = colors[i] if colors and i < len(colors) else default_colors[i % len(default_colors)]
        x = x_positions[i] if i < len(x_positions) else 0.7 + (i % 3) * 4.1
        y = y_positions[i] if i < len(y_positions) else 1.5 if i % 3 == 0 else (4.0 if i % 3 == 1 else 1.5)
        add_feature_card(slide, x, y, item_title, item_desc, color)
    
    return slide

def add_stats_slide(prs, title, stats_list):
    """添加数据统计幻灯片"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = RGBColor(248, 250, 252)
    bg_shape.line.fill.background()
    
    add_decorative_circles(slide)
    
    title_bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    title_bar.fill.solid()
    title_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
    title_bar.line.fill.background()
    
    title_box = slide.shapes.add_textbox(
        Inches(0.7), Inches(0.4),
        Inches(11.6), Inches(0.6)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    # 添加统计卡片
    colors = [RGBColor(59, 130, 246), RGBColor(168, 85, 247), RGBColor(251, 146, 60), RGBColor(34, 197, 94)]
    for i, (num, label) in enumerate(stats_list):
        x = 1.5 + i * 3.0
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(2),
            Inches(2.5), Inches(3)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = colors[i]
        card.line.fill.background()
        
        num_box = slide.shapes.add_textbox(
            Inches(x + 0.2), Inches(2.3),
            Inches(2.1), Inches(1)
        )
        tf = num_box.text_frame
        tf.paragraphs[0].text = num
        tf.paragraphs[0].font.size = Pt(42)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        label_box = slide.shapes.add_textbox(
            Inches(x + 0.2), Inches(3.5),
            Inches(2.1), Inches(1)
        )
        tf = label_box.text_frame
        tf.paragraphs[0].text = label
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    return slide

# 第1页：封面
add_title_slide(prs, "AI 英语学习助手", "智能陪伴，高效学习")

# 第2页：产品概览
slide = add_content_slide(prs, "产品概览", [
    ("少儿英语智能体", "专为3-12岁儿童设计\n互动游戏、趣味故事\n个性化学习计划"),
    ("口译训练智能体", "CATTI备考专家\n实时反馈、模拟考试\n专业训练方案"),
], [RGBColor(251, 146, 60), RGBColor(59, 130, 246)])

# 第3页：少儿英语智能体功能
add_content_slide(prs, "少儿英语智能体", [
    ("趣味对话练习", "50+日常场景\n生动有趣的对话"),
    ("绘本阅读", "海量英文绘本\nAI智能导读"),
    ("游戏化学习", "闯关模式\n收集勋章"),
    ("角色扮演", "职业体验\n场景模拟"),
    ("每日打卡", "养成习惯\n连续奖励"),
    ("成就系统", "成长记录\n激励机制"),
])

# 第4页：口译训练智能体功能
add_content_slide(prs, "口译训练智能体", [
    ("实时口译练习", "中英双向\n即时反馈"),
    ("CATTI真题模拟", "历年真题\n标准评分"),
    ("语音识别训练", "发音评测\n语调纠正"),
    ("笔记技巧指导", "速记方法\n符号系统"),
    ("AI智能评分", "多维度评估\n专业分析"),
    ("进步追踪", "能力报告\n提升建议"),
])

# 第5页：核心优势
add_stats_slide(prs, "核心优势", [
    ("24/7", "随时学习"),
    ("AI", "智能适配"),
    ("∞", "无限练习"),
    ("✓", "专业可靠"),
])

# 第6页：使用场景
add_content_slide(prs, "使用场景", [
    ("居家学习", "每天30分钟\n亲子互动"),
    ("通勤路上", "碎片时间\n高效利用"),
    ("考前冲刺", "查漏补缺\n高效备考"),
    ("亲子互动", "家长陪伴\n增进关系"),
    ("口语提升", "日常对话\n告别哑巴"),
    ("技能强化", "专项突破\n全面提升"),
])

# 第7页：使用流程
slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(slide_layout)

bg_shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0),
    prs.slide_width, prs.slide_height
)
bg_shape.fill.solid()
bg_shape.fill.fore_color.rgb = RGBColor(248, 250, 252)
bg_shape.line.fill.background()

add_decorative_circles(slide)

title_bar = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(0.3),
    Inches(12), Inches(0.8)
)
title_bar.fill.solid()
title_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
title_bar.line.fill.background()

title_box = slide.shapes.add_textbox(
    Inches(0.7), Inches(0.4),
    Inches(11.6), Inches(0.6)
)
tf = title_box.text_frame
tf.paragraphs[0].text = "使用流程"
tf.paragraphs[0].font.size = Pt(32)
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

steps = [
    ("1", "注册账号", "手机号一键注册"),
    ("2", "选择产品", "少儿英语/口译训练"),
    ("3", "开始学习", "AI智能引导学习"),
    ("4", "查看进度", "实时追踪效果"),
]

step_colors = [
    RGBColor(59, 130, 246),
    RGBColor(168, 85, 247),
    RGBColor(251, 146, 60),
    RGBColor(34, 197, 94),
]

for i, (num, title, desc) in enumerate(steps):
    x = 1.2 + i * 3.0
    
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x + 0.6), Inches(1.8),
        Inches(1.8), Inches(1.8)
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = step_colors[i]
    circle.line.fill.background()
    
    num_box = slide.shapes.add_textbox(
        Inches(x + 0.6), Inches(2.1),
        Inches(1.8), Inches(1)
    )
    tf = num_box.text_frame
    tf.paragraphs[0].text = num
    tf.paragraphs[0].font.size = Pt(44)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    title_box_step = slide.shapes.add_textbox(
        Inches(x), Inches(3.9),
        Inches(3), Inches(0.5)
    )
    tf = title_box_step.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(20)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(15, 23, 42)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    desc_box = slide.shapes.add_textbox(
        Inches(x), Inches(4.5),
        Inches(3), Inches(0.5)
    )
    tf = desc_box.text_frame
    tf.paragraphs[0].text = desc
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = RGBColor(107, 114, 128)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# 第8页：用户反馈
add_content_slide(prs, "用户反馈", [
    ("王妈妈", "孩子以前抵触英语\n现在每天主动学习"),
    ("李同学", "AI评分很专业\n顺利通过三级考试"),
    ("张老师", "推荐给学生\n效果显著"),
])

# 第9页：价格方案
add_content_slide(prs, "价格方案", [
    ("基础版 免费", "每日30分钟\n基础对话\n10个场景"),
    ("专业版 ¥99/月", "无限时长\n全部功能\nAI评分"),
    ("企业版 联系我们", "多账号\n定制内容\n专属支持"),
], [RGBColor(107, 114, 128), RGBColor(59, 130, 246), RGBColor(251, 146, 60)])

# 第10页：开始使用
slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(slide_layout)

bg_shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0),
    prs.slide_width, prs.slide_height
)
bg_shape.fill.solid()
bg_shape.fill.fore_color.rgb = RGBColor(15, 23, 42)
bg_shape.line.fill.background()

title_bg = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1.5), Inches(1.5),
    Inches(10), Inches(4)
)
title_bg.fill.solid()
title_bg.fill.fore_color.rgb = RGBColor(59, 130, 246)
title_bg.line.fill.background()

title_box = slide.shapes.add_textbox(
    Inches(2), Inches(2),
    Inches(9), Inches(1.2)
)
tf = title_box.text_frame
tf.paragraphs[0].text = "开始您的英语学习之旅"
tf.paragraphs[0].font.size = Pt(44)
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

subtitle_box = slide.shapes.add_textbox(
    Inches(1.5), Inches(3.8),
    Inches(10), Inches(0.8)
)
tf = subtitle_box.text_frame
tf.paragraphs[0].text = "立即体验AI智能学习助手，让学习更高效、更有趣！"
tf.paragraphs[0].font.size = Pt(24)
tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# 保存文件
output_path = "AI英语学习助手_美观版.pptx"
prs.save(output_path)
print(f"美观版PPT已生成: {output_path}")
