#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI英语学习助手 - PPT生成脚本
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

def add_title_slide(prs, title, subtitle):
    """添加标题幻灯片"""
    slide_layout = prs.slide_layouts[6]  # 空白布局
    slide = prs.slides.add_slide(slide_layout)
    
    # 添加背景色块
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(240, 240, 250)
    shape.line.fill.background()
    
    # 添加装饰圆
    circle1 = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(0.5), Inches(0.5),
        Inches(2), Inches(2)
    )
    circle1.fill.solid()
    circle1.fill.fore_color.rgb = RGBColor(59, 130, 246)
    circle1.line.fill.background()
    
    # 添加标题
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.5),
        Inches(12), Inches(1.5)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(54)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(59, 130, 246)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 添加副标题
    subtitle_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(4.2),
        Inches(12), Inches(1)
    )
    tf = subtitle_box.text_frame
    tf.paragraphs[0].text = subtitle
    tf.paragraphs[0].font.size = Pt(28)
    tf.paragraphs[0].font.color.rgb = RGBColor(107, 114, 128)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    return slide

def add_content_slide(prs, title, content_list, colors=None):
    """添加内容幻灯片"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # 添加标题
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(40)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(59, 130, 246)
    
    # 添加内容
    y_position = 1.3
    for i, (item_title, item_desc) in enumerate(content_list):
        # 颜色设置
        if colors and i < len(colors):
            bg_color = colors[i]
        else:
            bg_color = RGBColor(59, 130, 246)
        
        # 添加卡片背景
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.5 + (i % 3) * 4.2),
            Inches(y_position),
            Inches(4), Inches(2.5)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.fill.background()
        
        # 添加标题
        text_box = slide.shapes.add_textbox(
            Inches(0.7 + (i % 3) * 4.2),
            Inches(y_position + 0.2),
            Inches(3.6), Inches(0.6)
        )
        tf = text_box.text_frame
        tf.paragraphs[0].text = item_title
        tf.paragraphs[0].font.size = Pt(20)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        
        # 添加描述
        desc_box = slide.shapes.add_textbox(
            Inches(0.7 + (i % 3) * 4.2),
            Inches(y_position + 0.8),
            Inches(3.6), Inches(1.5)
        )
        tf = desc_box.text_frame
        tf.paragraphs[0].text = item_desc
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        tf.word_wrap = True
        
        if (i + 1) % 3 == 0:
            y_position += 2.8
    
    return slide

# 第1页：封面
add_title_slide(prs, "AI 英语学习助手", "智能陪伴，高效学习")

# 第2页：产品概览
slide = add_content_slide(prs, "产品概览", [
    ("少儿英语智能体", "专为3-12岁儿童设计的英语学习伙伴，通过互动游戏、趣味故事和个性化学习计划，让孩子在快乐中学习英语。"),
    ("口译训练智能体", "专业的CATTI二级和三级口译训练工具，提供实时反馈、模拟考试和个性化训练方案，助力口译备考。")
], [RGBColor(251, 146, 60), RGBColor(99, 102, 241)])

# 第3页：少儿英语智能体功能
add_content_slide(prs, "少儿英语智能体", [
    ("趣味对话练习", "生动有趣的日常对话，包含问候、购物、旅行等50+场景"),
    ("绘本阅读", "海量英文绘本，AI智能导读，单词解析，发音指导"),
    ("游戏化学习", "趣味闯关模式，收集勋章奖励，激发学习动力"),
    ("角色扮演", "模拟医生、老师、厨师等职业对话，提前体验社会"),
    ("每日打卡", "养成良好学习习惯，连续打卡获得神秘礼物"),
    ("成就系统", "丰富勋章墙，记录成长历程，激励持续学习")
], [RGBColor(251, 191, 36), RGBColor(251, 146, 60), RGBColor(34, 197, 94), 
    RGBColor(59, 130, 246), RGBColor(168, 85, 247), RGBColor(236, 72, 153)])

# 第4页：口译训练智能体功能
add_content_slide(prs, "口译训练智能体", [
    ("实时口译练习", "支持中英双向互译，智能识别发音，即时反馈纠错"),
    ("CATTI真题模拟", "涵盖二三级历年真题，严格按照官方标准评分"),
    ("语音识别训练", "专业语音评测，纠正发音语调，提升听力水平"),
    ("笔记技巧指导", "传授高效笔记方法，符号速记技巧，提升记录速度"),
    ("AI智能评分", "多维度评估：内容准确度、表达流畅度，专业术语"),
    ("进步追踪", "详细能力分析报告，薄弱环节诊断，个性化提升建议")
], [RGBColor(59, 130, 246), RGBColor(99, 102, 241), RGBColor(168, 85, 247),
    RGBColor(236, 72, 153), RGBColor(34, 197, 94), RGBColor(251, 146, 60)])

# 第5页：核心优势
add_content_slide(prs, "核心优势", [
    ("24/7 随时学习", "全天候AI陪伴，碎片化时间高效利用"),
    ("AI 智能适配", "AI精准分析，个性化学习方案定制"),
    ("无限练习", "海量训练素材，持续更新免费试用"),
    ("专业可靠", "资深教学团队，专业内容审核认证")
], [RGBColor(59, 130, 246), RGBColor(168, 85, 247), 
    RGBColor(251, 146, 60), RGBColor(34, 197, 94)])

# 第6页：使用场景
add_content_slide(prs, "使用场景", [
    ("居家学习", "每天30分钟，亲子互动时光"),
    ("通勤路上", "碎片时间利用，地铁公交随时学"),
    ("考前冲刺", "高效备考训练，查漏补缺"),
    ("亲子互动", "家长陪伴学习，增进亲子关系"),
    ("口语提升", "日常对话练习，告别哑巴英语"),
    ("技能强化", "专项能力突破，听说读写全提升")
], [RGBColor(59, 130, 246), RGBColor(168, 85, 247), RGBColor(251, 146, 60),
    RGBColor(34, 197, 94), RGBColor(99, 102, 241), RGBColor(236, 72, 153)])

# 第7页：使用流程
slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(slide_layout)
title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
tf = title_box.text_frame
tf.paragraphs[0].text = "使用流程"
tf.paragraphs[0].font.size = Pt(40)
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.color.rgb = RGBColor(59, 130, 246)

steps = [
    ("1", "注册账号", "手机号一键注册"),
    ("2", "选择产品", "少儿英语/口译训练"),
    ("3", "开始学习", "AI智能引导学习"),
    ("4", "查看进度", "实时追踪效果")
]

for i, (num, title, desc) in enumerate(steps):
    # 圆形编号
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.5 + i * 3),
        Inches(2),
        Inches(1.5), Inches(1.5)
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = RGBColor(59, 130, 246)
    circle.line.fill.background()
    
    # 编号文字
    num_box = slide.shapes.add_textbox(
        Inches(1.5 + i * 3), Inches(2.3),
        Inches(1.5), Inches(1)
    )
    tf = num_box.text_frame
    tf.paragraphs[0].text = num
    tf.paragraphs[0].font.size = Pt(36)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 步骤标题
    step_title = slide.shapes.add_textbox(
        Inches(1 + i * 3), Inches(3.8),
        Inches(2.5), Inches(0.5)
    )
    tf = step_title.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 步骤描述
    step_desc = slide.shapes.add_textbox(
        Inches(1 + i * 3), Inches(4.3),
        Inches(2.5), Inches(0.5)
    )
    tf = step_desc.text_frame
    tf.paragraphs[0].text = desc
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = RGBColor(107, 114, 128)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# 第8页：用户反馈
add_content_slide(prs, "用户反馈", [
    ("王妈妈", "孩子以前对英语很抵触，现在每天都主动要学进步非常明显！"),
    ("李同学", "口译训练功能太棒了！AI评分系统很专业，帮助我顺利通过了三级考试！"),
    ("张老师", "作为老师，我非常推荐！教学效果显著，学生们学习效率大幅提升。")
], [RGBColor(251, 146, 60), RGBColor(59, 130, 246), RGBColor(168, 85, 247)])

# 第9页：价格方案
add_content_slide(prs, "价格方案", [
    ("基础版 免费", "每日30分钟学习\n基础对话练习\n10个学习场景"),
    ("专业版 ¥99/月", "无限学习时长\n全部功能解锁\n500+学习场景\nAI智能评分"),
    ("企业版 联系我们", "多账号管理\n自定义学习内容\nAPI接口接入\n7*24专属支持")
], [RGBColor(107, 114, 128), RGBColor(59, 130, 246), RGBColor(251, 146, 60)])

# 第10页：开始使用
add_title_slide(prs, "开始您的英语学习之旅", "立即体验AI智能学习助手，让学习更高效、更有趣！")

# 保存文件
output_path = "AI英语学习助手_产品展示.pptx"
prs.save(output_path)
print(f"PPT已生成: {output_path}")
