#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能对话伙伴 - 创新版式PPT生成脚本
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 柔和配色定义
SOFT_BLUE = RGBColor(80, 120, 180)      # 柔和蓝色
SOFT_ORANGE = RGBColor(255, 150, 80)    # 柔和橙色
LIGHT_GRAY = RGBColor(248, 250, 252)    # 极浅灰
WHITE = RGBColor(255, 255, 255)
GRAY = RGBColor(120, 120, 120)
DARK_GRAY = RGBColor(80, 80, 80)

# 创建演示文稿
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def add_background(slide, color1, color2):
    """添加柔和背景"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color1
    bg.line.fill.background()
    
    # 添加柔和装饰
    circle1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11), Inches(0), Inches(4), Inches(4))
    circle1.fill.solid()
    circle1.fill.fore_color.rgb = color2
    circle1.line.fill.background()
    circle1.fill.transparency = 0.92
    
    circle2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1), Inches(4), Inches(3.5), Inches(3.5))
    circle2.fill.solid()
    circle2.fill.fore_color.rgb = color2
    circle2.line.fill.background()
    circle2.fill.transparency = 0.9

def add_subtle_card(slide, x, y, w, h, color, alpha=0.0):
    """添加柔和卡片效果 - 无边框，轻阴影"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = color
    card.line.fill.background()
    return card

def add_cover_slide():
    """第1页：创新封面"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_BLUE)
    
    # 大型柔和标题背景
    title_bg = add_subtle_card(slide, Inches(1.5), Inches(2.2), Inches(10.3), Inches(3), WHITE, 0.1)
    
    # 主标题
    title_box = slide.shapes.add_textbox(Inches(2), Inches(2.5), Inches(9.3), Inches(1.3))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "智能对话伙伴"
    tf.paragraphs[0].font.size = Pt(60)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 副标题
    subtitle_box = slide.shapes.add_textbox(Inches(2), Inches(4), Inches(9.3), Inches(0.8))
    tf = subtitle_box.text_frame
    tf.paragraphs[0].text = "少儿口语练习智能体 × 二三级口译智能体"
    tf.paragraphs[0].font.size = Pt(22)
    tf.paragraphs[0].font.color.rgb = GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 底部标语
    bottom_box = slide.shapes.add_textbox(Inches(2), Inches(6), Inches(9.3), Inches(0.6))
    tf = bottom_box.text_frame
    tf.paragraphs[0].text = "让语言学习更专业、更轻松"
    tf.paragraphs[0].font.size = Pt(20)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_overview_slide():
    """第2页：总览创新页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, WHITE, SOFT_ORANGE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "两大智能体，覆盖语言成长全阶段"
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 左边 - 少儿（柔和渐变）
    left_card = add_subtle_card(slide, Inches(0.8), Inches(1.6), Inches(5), Inches(4.5), RGBColor(255, 248, 240))
    
    left_title = slide.shapes.add_textbox(Inches(1), Inches(1.8), Inches(4.6), Inches(0.8))
    tf = left_title.text_frame
    tf.paragraphs[0].text = "少儿口语练习智能体"
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    left_desc = slide.shapes.add_textbox(Inches(1.2), Inches(2.8), Inches(4.2), Inches(2))
    tf = left_desc.text_frame
    tf.paragraphs[0].text = "兴趣启蒙\n自信开口\n游戏化学习\n激发表达欲"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.color.rgb = DARK_GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 右边 - 口译
    right_card = add_subtle_card(slide, Inches(7.5), Inches(1.6), Inches(5), Inches(4.5), RGBColor(240, 248, 255))
    
    right_title = slide.shapes.add_textbox(Inches(7.7), Inches(1.8), Inches(4.6), Inches(0.8))
    tf = right_title.text_frame
    tf.paragraphs[0].text = "二三级口译智能体"
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    right_desc = slide.shapes.add_textbox(Inches(7.9), Inches(2.8), Inches(4.2), Inches(2))
    tf = right_desc.text_frame
    tf.paragraphs[0].text = "专业进阶\n实战演练\n精准评估\n高效备考"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.color.rgb = DARK_GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 连接元素 - 隐形箭头
    arrow_box = slide.shapes.add_textbox(Inches(6), Inches(3.3), Inches(1.3), Inches(1))
    tf = arrow_box.text_frame
    tf.paragraphs[0].text = "→"
    tf.paragraphs[0].font.size = Pt(40)
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    bottom_text = slide.shapes.add_textbox(Inches(1.5), Inches(6.3), Inches(10.3), Inches(0.6))
    tf = bottom_text.text_frame
    tf.paragraphs[0].text = "从敢说到会译，每一步都有AI陪伴"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.color.rgb = GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_kids_intro_slide():
    """第3页：少儿智能体创新介绍"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_ORANGE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "少儿口语练习智能体 — 让孩子爱上说英语"
    tf.paragraphs[0].font.size = Pt(34)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 创新的三列布局 - 浮动式
    features = [
        ("场景对话", "模拟餐厅、动物园等丰富生活场景", "🎪"),
        ("语音打分", "实时纠正发音，像游戏一样轻松闯关", "⭐"),
        ("趣味激励", "动画勋章+成长树，持续激发动力", "🎯")
    ]
    
    for i, (title, desc, icon) in enumerate(features):
        x = Inches(1 + i * 4)
        y = Inches(1.6)
        
        # 柔和背景圆
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x-Inches(0.15), y, Inches(3.8), Inches(2))
        circle.fill.solid()
        circle.fill.fore_color.rgb = WHITE
        circle.line.fill.background()
        circle.fill.transparency = 0.2
        
        # 图标
        icon_box = slide.shapes.add_textbox(x+Inches(1.4), y+Inches(0.2), Inches(1), Inches(0.8))
        tf = icon_box.text_frame
        tf.paragraphs[0].text = icon
        tf.paragraphs[0].font.size = Pt(40)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 标题
        title_box = slide.shapes.add_textbox(x, y+Inches(1.2), Inches(3.5), Inches(0.6))
        tf = title_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(20)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 描述
        desc_box = slide.shapes.add_textbox(x-Inches(0.1), y+Inches(1.9), Inches(3.7), Inches(1.5))
        tf = desc_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(15)
        tf.paragraphs[0].font.color.rgb = DARK_GRAY
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    bottom_decor = slide.shapes.add_textbox(Inches(2), Inches(5.7), Inches(9.3), Inches(1))
    tf = bottom_decor.text_frame
    tf.paragraphs[0].text = "轻松开口 · 快乐成长"
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_kids_scenarios_slide():
    """第4页：少儿场景 - 创新布局"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, WHITE, SOFT_BLUE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "轻松融入学习日常"
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    scenarios = [
        ("🏠 家庭", "睡前10分钟，互动练习", "暖色调"),
        ("👨‍🏫 课堂", "老师的小助手，分组PK", "活力"),
        ("📚 自学", "孩子自己就能玩着学", "自由")
    ]
    
    positions = [(Inches(1.2), Inches(1.8)), (Inches(5.2), Inches(3)), (Inches(2.7), Inches(4.3))]
    
    for i, ((title, desc, tag), (x, y)) in enumerate(zip(scenarios, positions)):
        card = add_subtle_card(slide, x, y, Inches(7.9), Inches(1.6), RGBColor(248, 252, 255))
        
        t_box = slide.shapes.add_textbox(x+Inches(0.3), y+Inches(0.15), Inches(7.3), Inches(0.5))
        tf = t_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(22)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
        
        d_box = slide.shapes.add_textbox(x+Inches(0.5), y+Inches(0.7), Inches(6.9), Inches(0.8))
        tf = d_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.color.rgb = GRAY

def add_kids_workflow_slide():
    """第5页：少儿工作流 - 创新时间线"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_ORANGE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "一次开口，三步成长"
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    steps = [
        ("1 选择场景", "孩子挑选主题\n比如“在动物园”"),
        ("2 互动对话", "AI用卡通角色提问\n孩子语音回答"),
        ("3 反馈激励", "实时打分+收集勋章\n小树一天天长大")
    ]
    
    colors = [SOFT_ORANGE, RGBColor(255, 170, 100), RGBColor(255, 130, 70)]
    
    for i, (title, desc) in enumerate(steps):
        x = Inches(1.5 + i * 3.6)
        y = Inches(1.7)
        
        # 小圆点
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x+Inches(1.2), y, Inches(1), Inches(1))
        dot.fill.solid()
        dot.fill.fore_color.rgb = colors[i]
        dot.line.fill.background()
        
        dot_num = slide.shapes.add_textbox(x+Inches(1.2), y+Inches(0.2), Inches(1), Inches(0.6))
        tf = dot_num.text_frame
        tf.paragraphs[0].text = str(i+1)
        tf.paragraphs[0].font.size = Pt(26)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = WHITE
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 内容
        t_box = slide.shapes.add_textbox(x, y+Inches(1.2), Inches(3.4), Inches(0.6))
        tf = t_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(18)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = colors[i]
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        d_box = slide.shapes.add_textbox(x, y+Inches(1.9), Inches(3.4), Inches(1.3))
        tf = d_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.color.rgb = DARK_GRAY
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 连接线
        if i < 2:
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x+Inches(3.2), y+Inches(0.45), Inches(0.4), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = GRAY
            line.line.fill.background()
    
    bottom_text = slide.shapes.add_textbox(Inches(2), Inches(5.7), Inches(9.3), Inches(0.8))
    tf = bottom_text.text_frame
    tf.paragraphs[0].text = "每次3-5分钟，像玩游戏一样练口语"
    tf.paragraphs[0].font.size = Pt(22)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_interpreter_intro_slide():
    """第6页：口译智能体 - 创新介绍"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, WHITE, SOFT_BLUE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "二三级口译智能体 — 向专业口译迈进"
    tf.paragraphs[0].font.size = Pt(34)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    features = [
        ("双向交传模拟", "中英互译·自动分段录音", "🎧"),
        ("笔记法训练", "关键信息捕捉·重点提示", "📝"),
        ("考试真题演练", "覆盖CATTI二三级题型", "📚")
    ]
    
    for i, (title, desc, icon) in enumerate(features):
        x = Inches(1 + i * 4)
        y = Inches(1.6)
        
        # 柔和背景
        card_bg = add_subtle_card(slide, x, y, Inches(3.5), Inches(3.8), RGBColor(245, 250, 255))
        
        # 图标
        icon_box = slide.shapes.add_textbox(x+Inches(1.25), y+Inches(0.3), Inches(1), Inches(0.8))
        tf = icon_box.text_frame
        tf.paragraphs[0].text = icon
        tf.paragraphs[0].font.size = Pt(40)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 标题
        title_box = slide.shapes.add_textbox(x, y+Inches(1.3), Inches(3.5), Inches(0.5))
        tf = title_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(19)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_BLUE
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # 描述
        desc_box = slide.shapes.add_textbox(x+Inches(0.1), y+Inches(2), Inches(3.3), Inches(1.2))
        tf = desc_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.color.rgb = DARK_GRAY
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    bottom_text = slide.shapes.add_textbox(Inches(2), Inches(5.7), Inches(9.3), Inches(0.9))
    tf = bottom_text.text_frame
    tf.paragraphs[0].text = "专业AI陪练，让口译学习更高效"
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_interpreter_scenarios_slide():
    """第7页：口译场景 - 创新网格"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_BLUE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "备考与实战利器"
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    scenarios = [
        ("🌅 备考自习", "自由设定语速与停顿时间"),
        ("👥 课堂演练", "模拟会议口译，可复盘录音"),
        ("📊 自我评估", "AI给出准确率与流畅度分析")
    ]
    
    y_positions = [Inches(1.8), Inches(3.2), Inches(4.6)]
    
    for i, (title, desc) in enumerate(scenarios):
        card = add_subtle_card(slide, Inches(2.5), y_positions[i], Inches(8.3), Inches(1.3), WHITE)
        
        t_box = slide.shapes.add_textbox(Inches(2.7), y_positions[i]+Inches(0.1), Inches(7.9), Inches(0.5))
        tf = t_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(20)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_BLUE
        
        d_box = slide.shapes.add_textbox(Inches(3), y_positions[i]+Inches(0.65), Inches(7.3), Inches(0.6))
        tf = d_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(15)
        tf.paragraphs[0].font.color.rgb = GRAY

def add_interpreter_workflow_slide():
    """第8页：口译工作流 - 创新环形布局"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, WHITE, SOFT_ORANGE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "一段录音，四步进阶"
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    steps = [
        ("获取源语", "播放真题/上传音频"),
        ("口译录音", "提示音后开始口译"),
        ("AI评估", "三方面精准打分"),
        ("复盘学习", "对比译文·标记弱点")
    ]
    
    positions = [(Inches(1), Inches(1.8)), (Inches(7.3), Inches(1.8)), 
                 (Inches(7.3), Inches(4)), (Inches(1), Inches(4))]
    
    for i, (title, desc) in enumerate(steps):
        x, y = positions[i]
        
        # 柔和圆角块
        card = add_subtle_card(slide, x, y, Inches(5), Inches(1.9), RGBColor(248, 252, 255))
        
        num_box = slide.shapes.add_textbox(x+Inches(0.3), y+Inches(0.1), Inches(1), Inches(0.6))
        tf = num_box.text_frame
        tf.paragraphs[0].text = f"{i+1}"
        tf.paragraphs[0].font.size = Pt(24)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_BLUE
        
        t_box = slide.shapes.add_textbox(x+Inches(1.2), y+Inches(0.2), Inches(3.5), Inches(0.5))
        tf = t_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(18)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = SOFT_BLUE
        
        d_box = slide.shapes.add_textbox(x+Inches(1.2), y+Inches(0.9), Inches(3.5), Inches(0.9))
        tf = d_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.color.rgb = GRAY
    
    bottom_text = slide.shapes.add_textbox(Inches(2), Inches(6.1), Inches(9.3), Inches(0.7))
    tf = bottom_text.text_frame
    tf.paragraphs[0].text = "练一次，进步一次，随时回看成长曲线"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_comparison_slide():
    """第9页：对比与协作 - 创新双螺旋"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_BLUE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.35), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "一个家庭，两种需要 — 智能体如何一起使用？"
    tf.paragraphs[0].font.size = Pt(30)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 左边少儿
    left_card = add_subtle_card(slide, Inches(0.8), Inches(1.4), Inches(5.2), Inches(3.5), RGBColor(255, 248, 240))
    
    left_title = slide.shapes.add_textbox(Inches(1), Inches(1.55), Inches(4.8), Inches(0.6))
    tf = left_title.text_frame
    tf.paragraphs[0].text = "少儿口语"
    tf.paragraphs[0].font.size = Pt(26)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    left_desc = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(4.4), Inches(2))
    tf = left_desc.text_frame
    tf.paragraphs[0].text = "亲子共学，培养语感\n激发兴趣，自信开口\n为未来学习打下坚实基础"
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = DARK_GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 右边口译
    right_card = add_subtle_card(slide, Inches(7.3), Inches(1.4), Inches(5.2), Inches(3.5), RGBColor(240, 248, 255))
    
    right_title = slide.shapes.add_textbox(Inches(7.5), Inches(1.55), Inches(4.8), Inches(0.6))
    tf = right_title.text_frame
    tf.paragraphs[0].text = "二三级口译"
    tf.paragraphs[0].font.size = Pt(26)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    right_desc = slide.shapes.add_textbox(Inches(7.7), Inches(2.2), Inches(4.4), Inches(2))
    tf = right_desc.text_frame
    tf.paragraphs[0].text = "个人精进，职业跳板\n专业训练，高效备考\n实现翻译梦想的最佳助手"
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = DARK_GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 连接元素
    center_box = slide.shapes.add_textbox(Inches(5.8), Inches(2.6), Inches(1.7), Inches(1.1))
    tf = center_box.text_frame
    tf.paragraphs[0].text = "共同成长"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    bottom_text = slide.shapes.add_textbox(Inches(1.5), Inches(5.1), Inches(10.3), Inches(1.2))
    tf = bottom_text.text_frame
    tf.paragraphs[0].text = "从少儿到成人的语言能力进阶之路\n同一个账号，记录全周期成长轨迹"
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.color.rgb = DARK_GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_summary_slide():
    """第10页：总结与展望 - 创新三层"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, WHITE, SOFT_ORANGE)
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(11.3), Inches(0.9))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "让AI成为语言成长的终身伙伴"
    tf.paragraphs[0].font.size = Pt(38)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    points = [
        ("个性化", "匹配不同年龄与水平", SOFT_ORANGE),
        ("便捷性", "手机/平板/电脑随时用", SOFT_BLUE),
        ("未来计划", "增加手语翻译·方言适应", RGBColor(100, 160, 120))
    ]
    
    for i, (title, desc, color) in enumerate(points):
        y = Inches(1.6 + i * 1.5)
        card = add_subtle_card(slide, Inches(2.5), y, Inches(8.3), Inches(1.2), RGBColor(248, 250, 252))
        
        t_box = slide.shapes.add_textbox(Inches(2.7), y+Inches(0.1), Inches(7.9), Inches(0.5))
        tf = t_box.text_frame
        tf.paragraphs[0].text = title
        tf.paragraphs[0].font.size = Pt(22)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = color
        
        d_box = slide.shapes.add_textbox(Inches(3), y+Inches(0.65), Inches(7.3), Inches(0.5))
        tf = d_box.text_frame
        tf.paragraphs[0].text = desc
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.color.rgb = GRAY
    
    bottom_slogan = slide.shapes.add_textbox(Inches(2), Inches(6), Inches(9.3), Inches(0.9))
    tf = bottom_slogan.text_frame
    tf.paragraphs[0].text = "语言无界，成长可见"
    tf.paragraphs[0].font.size = Pt(30)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_thanks_slide():
    """第11页：感谢页 - 简洁温暖"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    add_background(slide, LIGHT_GRAY, SOFT_BLUE)
    
    # 大型柔和背景
    center_bg = add_subtle_card(slide, Inches(1.8), Inches(1.5), Inches(9.7), Inches(4.5), WHITE)
    
    title_box = slide.shapes.add_textbox(Inches(2.5), Inches(2), Inches(8.3), Inches(1.5))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "感谢聆听"
    tf.paragraphs[0].font.size = Pt(60)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_BLUE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    subtitle_box = slide.shapes.add_textbox(Inches(2.5), Inches(3.7), Inches(8.3), Inches(0.8))
    tf = subtitle_box.text_frame
    tf.paragraphs[0].text = "智能对话伙伴，陪伴每一次成长"
    tf.paragraphs[0].font.size = Pt(22)
    tf.paragraphs[0].font.color.rgb = GRAY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    qa_box = slide.shapes.add_textbox(Inches(2.5), Inches(4.7), Inches(8.3), Inches(1))
    tf = qa_box.text_frame
    tf.paragraphs[0].text = "Q&A"
    tf.paragraphs[0].font.size = Pt(30)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = SOFT_ORANGE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# 生成所有页面
add_cover_slide()
add_overview_slide()
add_kids_intro_slide()
add_kids_scenarios_slide()
add_kids_workflow_slide()
add_interpreter_intro_slide()
add_interpreter_scenarios_slide()
add_interpreter_workflow_slide()
add_comparison_slide()
add_summary_slide()
add_thanks_slide()

output_path = "智能对话伙伴_创新版式.pptx"
prs.save(output_path)
print(f"✅ 创新版式PPT已生成: {output_path}")
