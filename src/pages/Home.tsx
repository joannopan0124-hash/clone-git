import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Star, ArrowRight, BookOpen, GraduationCap, Users, Award, Play, MessageSquare, Globe, Clock, ShieldCheck, CheckCircle, Sparkles, Zap, Target, Mic, FileText, Brain, TrendingUp, Award as Medal, ThumbsUp, Calendar, Crown, Heart, Gift } from 'lucide-react';

const slides = [
  { id: 1, title: 'AI 英语学习助手', subtitle: '智能陪伴，高效学习', type: 'cover' },
  { id: 2, title: '产品概览', type: 'overview' },
  { id: 3, title: '少儿英语智能体', type: 'kids' },
  { id: 4, title: '口译训练智能体', type: 'interpreter' },
  { id: 5, title: '核心优势', type: 'advantages' },
  { id: 6, title: '使用场景', type: 'use-cases' },
  { id: 7, title: '使用流程', type: 'how-to' },
  { id: 8, title: '用户反馈', type: 'testimonials' },
  { id: 9, title: '价格方案', type: 'pricing' },
  { id: 10, title: '开始使用', type: 'contact' }
];

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(prev => prev + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentSlide]);

  const Slide1 = () => (
    <div className="h-full flex flex-col items-center justify-center text-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 opacity-20"></div>
      <div className="absolute top-20 left-20 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-20 right-20 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }}></div>
      
      <div className="relative z-10">
        <div className="flex gap-4 justify-center mb-8 animate-fade-in">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-xl">
            <BookOpen className="w-10 h-10 text-white" />
          </div>
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-xl">
            <Globe className="w-10 h-10 text-white" />
          </div>
        </div>
        <h1 className="text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-6 animate-fade-in">
          AI 英语学习助手
        </h1>
        <p className="text-3xl text-gray-600 mb-8 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          智能陪伴，高效学习
        </p>
        <div className="flex gap-6 justify-center animate-fade-in" style={{ animationDelay: '0.6s' }}>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl px-6 py-3 shadow-lg">
            <span className="text-2xl font-bold text-blue-600">10,000+</span>
            <p className="text-gray-600 text-sm">活跃用户</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl px-6 py-3 shadow-lg">
            <span className="text-2xl font-bold text-purple-600">95%</span>
            <p className="text-gray-600 text-sm">满意度</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl px-6 py-3 shadow-lg">
            <span className="text-2xl font-bold text-pink-600">24/7</span>
            <p className="text-gray-600 text-sm">全天候服务</p>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-10 text-gray-400 animate-bounce">
        <p className="text-sm mb-2">点击右侧箭头继续</p>
        <ChevronRight className="w-8 h-8 mx-auto" />
      </div>
    </div>
  );

  const Slide2 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-16">
        产品概览
      </h2>
      <div className="grid md:grid-cols-2 gap-12 max-w-6xl">
        <div className="bg-gradient-to-br from-orange-50 via-yellow-50 to-amber-50 rounded-3xl p-10 border-2 border-orange-200 hover:shadow-2xl transition-all duration-500 hover:-translate-y-3">
          <div className="w-24 h-24 bg-gradient-to-br from-orange-400 to-yellow-400 rounded-2xl flex items-center justify-center mb-8 shadow-lg">
            <Users className="w-12 h-12 text-white" />
          </div>
          <h3 className="text-3xl font-bold text-gray-800 mb-4">少儿英语智能体</h3>
          <p className="text-gray-600 text-lg leading-relaxed mb-6">
            专为3-12岁儿童设计的英语学习伙伴，通过互动游戏、趣味故事和个性化学习计划，让孩子在快乐中学习英语。
          </p>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">趣味互动对话</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">绘本智能导读</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">游戏化学习</span>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-3xl p-10 border-2 border-blue-200 hover:shadow-2xl transition-all duration-500 hover:-translate-y-3">
          <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-indigo-400 rounded-2xl flex items-center justify-center mb-8 shadow-lg">
            <GraduationCap className="w-12 h-12 text-white" />
          </div>
          <h3 className="text-3xl font-bold text-gray-800 mb-4">口译训练智能体</h3>
          <p className="text-gray-600 text-lg leading-relaxed mb-6">
            专业的CATTI二级和三级口译训练工具，提供实时反馈、模拟考试和个性化训练方案，助力口译备考。
          </p>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">真题模拟训练</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">AI智能评分</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">实时翻译反馈</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const Slide3 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-500 mb-8">
        少儿英语智能体
      </h2>
      <p className="text-xl text-gray-600 mb-12 text-center max-w-3xl">
        专为儿童设计，让英语学习变得有趣、有效！
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl">
        {[
          { icon: MessageSquare, title: '趣味对话练习', desc: '生动有趣的日常对话，包含问候、购物、旅行等50+场景' },
          { icon: BookOpen, title: '绘本阅读', desc: '海量英文绘本，AI智能导读，单词解析，发音指导' },
          { icon: Sparkles, title: '游戏化学习', desc: '趣味闯关模式，收集勋章奖励，激发学习动力' },
          { icon: Users, title: '角色扮演', desc: '模拟医生、老师、厨师等职业对话，提前体验社会' },
          { icon: Clock, title: '每日打卡', desc: '养成良好学习习惯，连续打卡获得神秘礼物' },
          { icon: Award, title: '成就系统', desc: '丰富勋章墙，记录成长历程，激励持续学习' }
        ].map((item, index) => (
          <div key={index} className="bg-white rounded-2xl p-8 shadow-xl border-2 border-orange-100 hover:border-orange-300 transition-all duration-300 hover:scale-105 hover:shadow-2xl">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-100 to-yellow-100 rounded-xl flex items-center justify-center mb-6">
              <item.icon className="w-8 h-8 text-orange-500" />
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-3">{item.title}</h4>
            <p className="text-gray-600">{item.desc}</p>
          </div>
        ))}
      </div>
      <div className="mt-10 flex gap-6">
        <div className="bg-orange-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-orange-600">500+</div>
          <div className="text-gray-600 text-sm">学习场景</div>
        </div>
        <div className="bg-yellow-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-yellow-600">1000+</div>
          <div className="text-gray-600 text-sm">英文绘本</div>
        </div>
        <div className="bg-amber-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-amber-600">50+</div>
          <div className="text-gray-600 text-sm">游戏关卡</div>
        </div>
      </div>
    </div>
  );

  const Slide4 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-indigo-500 mb-8">
        口译训练智能体
      </h2>
      <p className="text-xl text-gray-600 mb-12 text-center max-w-3xl">
        专业口译备考助手，助您顺利通过CATTI考试！
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl">
        {[
          { icon: Play, title: '实时口译练习', desc: '支持中英双向互译，智能识别发音，即时反馈纠错' },
          { icon: Target, title: 'CATTI真题模拟', desc: '涵盖二三级历年真题，严格按照官方标准评分' },
          { icon: Mic, title: '语音识别训练', desc: '专业语音评测，纠正发音语调，提升听力水平' },
          { icon: FileText, title: '笔记技巧指导', desc: '传授高效笔记方法，符号速记技巧，提升记录速度' },
          { icon: Brain, title: 'AI智能评分', desc: '多维度评估：内容准确度、表达流畅度、专业术语' },
          { icon: TrendingUp, title: '进步追踪', desc: '详细能力分析报告，薄弱环节诊断，个性化提升建议' }
        ].map((item, index) => (
          <div key={index} className="flex gap-6 items-start bg-white rounded-2xl p-8 shadow-xl border-2 border-blue-100">
            <div className="w-18 h-18 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center shrink-0">
              <item.icon className="w-9 h-9 text-blue-500" />
            </div>
            <div>
              <h4 className="text-xl font-bold text-gray-800 mb-3">{item.title}</h4>
              <p className="text-gray-600">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-10 grid grid-cols-3 gap-6">
        <div className="bg-blue-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-blue-600">88%</div>
          <div className="text-gray-600 text-sm">考试通过率</div>
        </div>
        <div className="bg-indigo-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-indigo-600">500+</div>
          <div className="text-gray-600 text-sm">真题题库</div>
        </div>
        <div className="bg-purple-100 rounded-xl px-6 py-4 text-center">
          <div className="text-3xl font-bold text-purple-600">AI</div>
          <div className="text-gray-600 text-sm">智能评分系统</div>
        </div>
      </div>
    </div>
  );

  const Slide5 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-gray-800 mb-16">核心优势</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-7xl">
        {[
          { num: '24/7', title: '随时学习', desc: '全天候AI陪伴，碎片化时间高效利用', color: 'from-blue-400 to-cyan-400' },
          { num: 'AI', title: '智能适配', desc: 'AI精准分析，个性化学习方案定制', color: 'from-purple-400 to-pink-400' },
          { num: '∞', title: '无限练习', desc: '海量训练素材，持续更新免费试用', color: 'from-orange-400 to-yellow-400' },
          { num: '✓', title: '专业可靠', desc: '资深教学团队，专业内容审核认证', color: 'from-green-400 to-emerald-400' }
        ].map((item, index) => (
          <div key={index} className={`bg-gradient-to-br ${item.color} rounded-3xl p-10 text-white hover:scale-105 transition-all duration-300 shadow-xl`}>
            <div className="text-6xl font-extrabold mb-4">{item.num}</div>
            <h4 className="text-2xl font-bold mb-3">{item.title}</h4>
            <p className="text-white/90">{item.desc}</p>
          </div>
        ))}
      </div>
      
      <div className="mt-16 grid grid-cols-3 gap-8 max-w-5xl">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 text-center border-2 border-blue-100">
          <div className="text-5xl font-bold text-blue-600 mb-3">95%</div>
          <p className="text-gray-600 text-lg">少儿用户满意度</p>
          <p className="text-gray-500 text-sm mt-2">超过10000名家长推荐</p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 text-center border-2 border-purple-100">
          <div className="text-5xl font-bold text-purple-600 mb-3">88%</div>
          <p className="text-gray-600 text-lg">口译考试通过率</p>
          <p className="text-gray-500 text-sm mt-2">历年通过率统计</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 text-center border-2 border-green-100">
          <div className="text-5xl font-bold text-green-600 mb-3">10K+</div>
          <p className="text-gray-600 text-lg">活跃学习用户</p>
          <p className="text-gray-500 text-sm mt-2">覆盖全国各省市</p>
        </div>
      </div>
    </div>
  );

  const Slide6 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-gray-800 mb-16">使用场景</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl">
        {[
          { title: '居家学习', time: '每天30分钟', desc: '亲子互动时光', color: 'from-blue-400 to-cyan-400', icon: Home },
          { title: '通勤路上', time: '碎片时间利用', desc: '地铁公交随时学', color: 'from-purple-400 to-pink-400', icon: Globe },
          { title: '考前冲刺', time: '高效备考训练', desc: '查漏补缺', color: 'from-orange-400 to-yellow-400', icon: Target },
          { title: '亲子互动', time: '家长陪伴学习', desc: '增进亲子关系', color: 'from-green-400 to-emerald-400', icon: Heart },
          { title: '口语提升', time: '日常对话练习', desc: '告别哑巴英语', color: 'from-indigo-400 to-violet-400', icon: Mic },
          { title: '技能强化', time: '专项能力突破', desc: '听说读写全提升', color: 'from-rose-400 to-red-400', icon: TrendingUp }
        ].map((item, index) => (
          <div key={index} className={`bg-gradient-to-br ${item.color} rounded-3xl p-10 text-white hover:scale-105 transition-transform duration-300 shadow-xl`}>
            <item.icon className="w-12 h-12 mb-6" />
            <h4 className="text-3xl font-bold mb-3">{item.title}</h4>
            <p className="text-xl mb-2">{item.time}</p>
            <p className="text-white/80">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide7 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-gray-800 mb-16">使用流程</h2>
      <div className="flex items-center justify-center gap-6 max-w-7xl">
        {[
          { step: '1', title: '注册账号', desc: '手机号一键注册', icon: Users },
          { step: '2', title: '选择产品', desc: '少儿英语/口译训练', icon: BookOpen },
          { step: '3', title: '开始学习', desc: 'AI智能引导学习', icon: Brain },
          { step: '4', title: '查看进度', desc: '实时追踪效果', icon: TrendingUp }
        ].map((item, index) => (
          <React.Fragment key={index}>
            <div className="text-center">
              <div className="w-28 h-28 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-5xl font-bold text-white mb-6 mx-auto shadow-xl">
                {item.step}
              </div>
              <h4 className="text-2xl font-bold text-gray-800 mb-2">{item.title}</h4>
              <p className="text-gray-600">{item.desc}</p>
            </div>
            {index < 3 && (
              <div className="flex flex-col items-center">
                <ArrowRight className="w-12 h-12 text-blue-300" />
                <span className="text-sm text-gray-400 mt-2">步骤 {index + 1}</span>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
      <div className="mt-16 bg-gradient-to-r from-blue-50 to-purple-50 rounded-3xl p-10 max-w-4xl">
        <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">三分钟快速上手</h3>
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-500 mb-2">1分钟</div>
            <p className="text-gray-600">完成账号注册</p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-500 mb-2">1分钟</div>
            <p className="text-gray-600">选择学习目标</p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-pink-500 mb-2">1分钟</div>
            <p className="text-gray-600">开始第一次学习</p>
          </div>
        </div>
      </div>
    </div>
  );

  const Slide8 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-gray-800 mb-16">用户反馈</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl">
        {[
          { 
            name: '王妈妈', 
            role: '8岁孩子家长', 
            rating: 5, 
            text: '孩子以前对英语很抵触，现在每天都主动要学进步非常明显！口语表达自信多了。', 
            color: 'from-orange-50 to-yellow-50',
            avatar: '👩'
          },
          { 
            name: '李同学', 
            role: 'CATTI三级考生', 
            rating: 5, 
            text: '口译训练功能太棒了！AI评分系统很专业，帮助我顺利通过了三级考试！',
            color: 'from-blue-50 to-indigo-50',
            avatar: '👨‍🎓'
          },
          { 
            name: '张老师', 
            role: '中学英语教师', 
            rating: 5, 
            text: '作为老师，我非常推荐！教学效果显著，学生们学习效率大幅提升，成绩进步明显。',
            color: 'from-purple-50 to-pink-50',
            avatar: '👩‍🏫'
          }
        ].map((item, index) => (
          <div key={index} className={`bg-gradient-to-br ${item.color} rounded-3xl p-10 border-2 border-gray-100 shadow-xl`}>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-3xl">
                {item.avatar}
              </div>
              <div>
                <div className="font-bold text-gray-800 text-xl">{item.name}</div>
                <div className="text-gray-500">{item.role}</div>
              </div>
            </div>
            <div className="flex mb-4">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-7 h-7 text-yellow-400 fill-current" />
              ))}
            </div>
            <p className="text-gray-700 text-lg leading-relaxed italic">"{item.text}"</p>
          </div>
        ))}
      </div>
      <div className="mt-12 flex gap-6">
        <div className="flex items-center gap-2">
          <ThumbsUp className="w-6 h-6 text-green-500" />
          <span className="text-gray-700">好评率 98%</span>
        </div>
        <div className="flex items-center gap-2">
          <Medal className="w-6 h-6 text-blue-500" />
          <span className="text-gray-700">用户推荐指数 9.5</span>
        </div>
      </div>
    </div>
  );

  const Slide9 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-6xl font-bold text-gray-800 mb-16">价格方案</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-7xl">
        {[
          { 
            name: '基础版', 
            price: '免费', 
            features: [
              '每日30分钟学习',
              '基础对话练习',
              '10个学习场景',
              '5本英文绘本',
              '基础发音评测',
              '学习进度追踪'
            ], 
            popular: false,
            color: 'from-gray-400 to-gray-500'
          },
          { 
            name: '专业版', 
            price: '¥99/月', 
            features: [
              '无限学习时长',
              '全部功能解锁',
              '500+学习场景',
              '1000+英文绘本',
              'AI智能评分',
              '专属学习报告',
              '优先客服支持',
              '离线下载功能'
            ], 
            popular: true,
            color: 'from-blue-500 to-purple-500'
          },
          { 
            name: '企业版', 
            price: '联系我们', 
            features: [
              '多账号管理',
              '自定义学习内容',
              'API接口接入',
              '专属培训服务',
              '数据统计分析',
              '7*24专属支持',
              '定制开发服务',
              '年度套餐优惠'
            ], 
            popular: false,
            color: 'from-orange-500 to-red-500'
          }
        ].map((plan, index) => (
          <div key={index} className={`relative rounded-3xl p-10 transition-all duration-300 ${plan.popular ? `bg-gradient-to-br ${plan.color} text-white scale-105 shadow-2xl` : 'bg-white border-4 border-gray-200 hover:border-blue-300 shadow-xl'}`}>
            {plan.popular && (
              <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-orange-400 text-white px-8 py-2 rounded-full text-lg font-bold shadow-lg">
                ⭐ 最受欢迎
              </div>
            )}
            <h3 className="text-3xl font-bold mb-4">{plan.name}</h3>
            <div className="text-5xl font-extrabold mb-8">{plan.price}</div>
            <ul className="space-y-4 mb-10">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-center gap-3">
                  <CheckCircle className={`w-6 h-6 ${plan.popular ? 'text-yellow-300' : 'text-green-500'}`} />
                  <span className={plan.popular ? 'text-white/95' : 'text-gray-700'}>{feature}</span>
                </li>
              ))}
            </ul>
            <button className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300 ${plan.popular ? 'bg-white text-blue-600 hover:bg-gray-100 shadow-lg' : `bg-gradient-to-r ${plan.color} text-white hover:shadow-xl`}`}>
              {plan.name === '企业版' ? '获取报价' : '立即购买'}
            </button>
          </div>
        ))}
      </div>
      <p className="mt-8 text-gray-500 text-center">* 所有套餐均支持7天无理由退款</p>
    </div>
  );

  const Slide10 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <div className="text-center max-w-4xl">
        <div className="flex gap-4 justify-center mb-8">
          <Gift className="w-16 h-16 text-pink-500" />
          <Crown className="w-16 h-16 text-yellow-500" />
          <Sparkles className="w-16 h-16 text-purple-500" />
        </div>
        <h2 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-8">
          开始您的英语学习之旅
        </h2>
        <p className="text-2xl text-gray-600 mb-12">
          立即体验AI智能学习助手，让学习更高效、更有趣！
        </p>
        
        <div className="flex gap-8 justify-center mb-16">
          <a href="https://www.coze.cn/s/llxv2V1cxnQ/" target="_blank" rel="noopener noreferrer" className="px-16 py-6 bg-gradient-to-r from-orange-500 to-yellow-500 text-white text-2xl font-bold rounded-2xl hover:shadow-2xl transition-all duration-300 hover:scale-105">
            🧸 少儿英语智能体
          </a>
          <a href="https://www.coze.cn/s/i-ipKPU1uDk/" target="_blank" rel="noopener noreferrer" className="px-16 py-6 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-2xl font-bold rounded-2xl hover:shadow-2xl transition-all duration-300 hover:scale-105">
            🎓 口译训练智能体
          </a>
        </div>
        
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-3xl p-10 inline-block">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">联系我们</h3>
          <div className="space-y-4 text-left">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📧</span>
              <span className="text-gray-700">contact@example.com</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl">📱</span>
              <span className="text-gray-700">400-888-8888</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl">💬</span>
              <span className="text-gray-700">微信公众号: AI英语学习</span>
            </div>
          </div>
          <div className="mt-6">
            <p className="text-gray-500 mb-3">扫码关注公众号</p>
            <div className="w-32 h-32 bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl mx-auto flex items-center justify-center border-2 border-gray-300">
              <span className="text-gray-400 text-sm">二维码</span>
            </div>
          </div>
        </div>
        
        <div className="mt-12 text-gray-400">
          <p className="text-lg">感谢您的关注与支持！</p>
          <p className="text-sm mt-2">让AI成为您英语学习路上的得力助手</p>
        </div>
      </div>
    </div>
  );

  const renderSlide = () => {
    switch (currentSlide) {
      case 0: return <Slide1 />;
      case 1: return <Slide2 />;
      case 2: return <Slide3 />;
      case 3: return <Slide4 />;
      case 4: return <Slide5 />;
      case 5: return <Slide6 />;
      case 6: return <Slide7 />;
      case 7: return <Slide8 />;
      case 8: return <Slide9 />;
      case 9: return <Slide10 />;
      default: return <Slide1 />;
    }
  };

  return (
    <div className="min-h-screen bg-white relative">
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.6s ease-out forwards;
        }
      `}</style>
      
      <div className="h-screen w-full relative">
        {renderSlide()}
        
        {currentSlide > 0 && (
          <button
            onClick={prevSlide}
            className="absolute left-8 top-1/2 -translate-y-1/2 w-16 h-16 bg-white rounded-full shadow-xl flex items-center justify-center hover:bg-gray-50 hover:scale-110 transition-all duration-300 z-20 border-2 border-gray-200"
          >
            <ChevronLeft className="w-8 h-8 text-gray-700" />
          </button>
        )}
        
        {currentSlide < slides.length - 1 && (
          <button
            onClick={nextSlide}
            className="absolute right-8 top-1/2 -translate-y-1/2 w-16 h-16 bg-white rounded-full shadow-xl flex items-center justify-center hover:bg-gray-50 hover:scale-110 transition-all duration-300 z-20 border-2 border-gray-200"
          >
            <ChevronRight className="w-8 h-8 text-gray-700" />
          </button>
        )}
        
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`h-3 rounded-full transition-all duration-300 ${index === currentSlide ? 'bg-gradient-to-r from-blue-500 to-purple-500 w-12' : 'bg-gray-300 hover:bg-gray-400 w-3'}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
