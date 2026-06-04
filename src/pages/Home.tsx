import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Star, ArrowRight, BookOpen, GraduationCap, Users, Award, Play, MessageSquare, Globe, Clock, ShieldCheck, CheckCircle, XCircle, Sparkles, Zap, Target } from 'lucide-react';

const slides = [
  {
    id: 1,
    title: 'AI 英语学习助手',
    subtitle: '智能陪伴，高效学习',
    type: 'cover'
  },
  {
    id: 2,
    title: '产品概览',
    type: 'overview'
  },
  {
    id: 3,
    title: '少儿英语智能体',
    type: 'kids'
  },
  {
    id: 4,
    title: '口译训练智能体',
    type: 'interpreter'
  },
  {
    id: 5,
    title: '核心优势',
    type: 'advantages'
  },
  {
    id: 6,
    title: '使用场景',
    type: 'use-cases'
  },
  {
    id: 7,
    title: '使用流程',
    type: 'how-to'
  },
  {
    id: 8,
    title: '用户反馈',
    type: 'testimonials'
  },
  {
    id: 9,
    title: '价格方案',
    type: 'pricing'
  },
  {
    id: 10,
    title: '开始使用',
    type: 'contact'
  }
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
      <div className="absolute inset-0 bg-gradient-to-br from-gray-400 via-gray-500 to-gray-600 opacity-20"></div>
      <div className="absolute top-20 left-20 w-72 h-72 bg-gray-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-20 right-20 w-72 h-72 bg-gray-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }}></div>
      
      <div className="relative z-10">
        <h1 className="text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-800 to-gray-900 mb-6 animate-fade-in">
          AI 英语学习助手
        </h1>
        <p className="text-2xl text-gray-600 mb-12 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          智能陪伴，高效学习
        </p>
        <div className="flex gap-4 justify-center animate-fade-in" style={{ animationDelay: '0.6s' }}>
          <div className="w-16 h-16 bg-gradient-to-br from-gray-700 to-gray-800 rounded-full flex items-center justify-center">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <div className="w-16 h-16 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center">
            <Globe className="w-8 h-8 text-white" />
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
      <h2 className="text-5xl font-bold text-gray-800 mb-16">产品概览</h2>
      <div className="grid md:grid-cols-2 gap-8 max-w-5xl">
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-3xl p-8 border border-gray-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
          <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-700 rounded-2xl flex items-center justify-center mb-6">
            <Users className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">少儿英语智能体</h3>
          <p className="text-gray-600 text-lg leading-relaxed">
            专为儿童设计的英语学习伙伴，通过互动游戏、趣味故事和个性化学习计划，让孩子在快乐中学习英语。
          </p>
        </div>
        
        <div className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-3xl p-8 border border-gray-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
          <div className="w-20 h-20 bg-gradient-to-br from-gray-700 to-gray-800 rounded-2xl flex items-center justify-center mb-6">
            <GraduationCap className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">口译训练智能体</h3>
          <p className="text-gray-600 text-lg leading-relaxed">
            专业的二级和三级口译训练工具，提供实时反馈、模拟考试和个性化训练方案，助力口译备考。
          </p>
        </div>
      </div>
    </div>
  );

  const Slide3 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900 mb-12">
        少儿英语智能体
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl">
        {[
          { icon: MessageSquare, title: '趣味对话', desc: '生动有趣的日常对话练习' },
          { icon: BookOpen, title: '绘本阅读', desc: '海量英文绘本，智能导读' },
          { icon: Sparkles, title: '游戏学习', desc: '边玩边学，激发兴趣' },
          { icon: Users, title: '角色扮演', desc: '多种场景模拟对话' },
          { icon: Clock, title: '每日打卡', desc: '培养良好学习习惯' },
          { icon: Award, title: '成就系统', desc: '鼓励孩子持续学习' }
        ].map((item, index) => (
          <div key={index} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:border-gray-400 transition-all duration-300 hover:scale-105">
            <div className="w-14 h-14 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl flex items-center justify-center mb-4">
              <item.icon className="w-7 h-7 text-gray-700" />
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h4>
            <p className="text-gray-600">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide4 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900 mb-12">
        口译训练智能体
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl">
        {[
          { icon: Play, title: '实时口译练习', desc: '支持中英双向互译，即时反馈' },
          { icon: Target, title: '真题模拟', desc: 'CATTI二级、三级真题训练' },
          { icon: Zap, title: '速度训练', desc: '提升口译反应速度' },
          { icon: ShieldCheck, title: '专业评估', desc: 'AI智能评分，专业分析' },
          { icon: Clock, title: '计时训练', desc: '严格按照考试时间要求' },
          { icon: Award, title: '能力报告', desc: '详细的能力分析和提升建议' }
        ].map((item, index) => (
          <div key={index} className="flex gap-6 items-start bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
            <div className="w-16 h-16 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl flex items-center justify-center shrink-0">
              <item.icon className="w-8 h-8 text-gray-700" />
            </div>
            <div>
              <h4 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h4>
              <p className="text-gray-600">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide5 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-gray-800 mb-12">核心优势</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-6xl">
        {[
          { num: '24/7', title: '随时学习', desc: '全天候智能陪伴' },
          { num: 'AI', title: '智能适配', desc: '个性化学习方案' },
          { num: '∞', title: '无限练习', desc: '海量训练素材' },
          { num: '✓', title: '专业可靠', desc: '专业教学团队打造' }
        ].map((item, index) => (
          <div key={index} className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 text-center border border-gray-200 hover:shadow-xl transition-all duration-300">
            <div className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900 mb-4">
              {item.num}
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h4>
            <p className="text-gray-600">{item.desc}</p>
          </div>
        ))}
      </div>
      
      <div className="mt-12 grid grid-cols-2 gap-8 max-w-4xl">
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-700 mb-2">95%</div>
          <p className="text-gray-600">少儿用户满意度</p>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-800 mb-2">88%</div>
          <p className="text-gray-600">口译考试通过率</p>
        </div>
      </div>
    </div>
  );

  const Slide6 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-gray-800 mb-12">使用场景</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl">
        {[
          { title: '居家学习', time: '每天30分钟', color: 'from-gray-400 to-gray-500' },
          { title: '通勤路上', time: '碎片时间利用', color: 'from-gray-500 to-gray-600' },
          { title: '考前冲刺', time: '高效备考训练', color: 'from-gray-600 to-gray-700' },
          { title: '亲子互动', time: '家长陪伴学习', color: 'from-gray-700 to-gray-800' },
          { title: '口语提升', time: '日常对话练习', color: 'from-gray-400 to-gray-600' },
          { title: '技能强化', time: '专项能力突破', color: 'from-gray-500 to-gray-700' }
        ].map((item, index) => (
          <div key={index} className={`bg-gradient-to-br ${item.color} rounded-2xl p-8 text-white hover:scale-105 transition-transform duration-300 shadow-xl`}>
            <h4 className="text-2xl font-bold mb-4">{item.title}</h4>
            <p className="text-white/90">{item.time}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide7 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-gray-800 mb-16">使用流程</h2>
      <div className="flex items-center justify-center gap-4 max-w-4xl">
        {[
          { step: '1', title: '注册账号', desc: '简单几步即可开始' },
          { step: '2', title: '选择产品', desc: '少儿英语或口译训练' },
          { step: '3', title: '开始学习', desc: 'AI智能引导学习' },
          { step: '4', title: '查看进度', desc: '实时追踪学习效果' }
        ].map((item, index) => (
          <React.Fragment key={index}>
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center text-3xl font-bold text-white mb-4 mx-auto shadow-lg">
                {item.step}
              </div>
              <h4 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h4>
              <p className="text-gray-600">{item.desc}</p>
            </div>
            {index < 3 && <ArrowRight className="w-10 h-10 text-gray-300" />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );

  const Slide8 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-gray-800 mb-12">用户反馈</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl">
        {[
          { name: '王妈妈', role: '6岁孩子家长', rating: 5, text: '孩子现在每天都主动要学英语，进步非常明显！', color: 'from-gray-50 to-gray-100' },
          { name: '李同学', role: 'CATTI备考', rating: 5, text: '口译训练功能太棒了，帮我顺利通过了三级考试！', color: 'from-gray-100 to-gray-200' },
          { name: '张老师', role: '英语教师', rating: 5, text: '推荐给学生们使用，效果非常好，学习效率大幅提升。', color: 'from-gray-200 to-gray-300' }
        ].map((item, index) => (
          <div key={index} className={`bg-gradient-to-br ${item.color} rounded-2xl p-8 border border-gray-200`}>
            <div className="flex mb-4">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-6 h-6 text-gray-500 fill-current" />
              ))}
            </div>
            <p className="text-gray-700 text-lg mb-6 italic">"{item.text}"</p>
            <div>
              <div className="font-bold text-gray-800">{item.name}</div>
              <div className="text-gray-500 text-sm">{item.role}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide9 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <h2 className="text-5xl font-bold text-gray-800 mb-12">价格方案</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
        {[
          { name: '基础版', price: '免费', features: ['基础对话', '部分素材', '每日30分钟'], popular: false },
          { name: '专业版', price: '¥99/月', features: ['全部功能', '无限时长', '专属客服', '学习报告'], popular: true },
          { name: '企业版', price: '联系我们', features: ['多账号管理', '定制服务', 'API接入', '专属支持'], popular: false }
        ].map((plan, index) => (
          <div key={index} className={`relative rounded-3xl p-8 transition-all duration-300 ${plan.popular ? 'bg-gradient-to-br from-gray-700 to-gray-900 text-white scale-105 shadow-2xl' : 'bg-white border-2 border-gray-300 hover:border-gray-500'}`}>
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-4 py-1 rounded-full text-sm font-bold">
                最受欢迎
              </div>
            )}
            <h3 className="text-2xl font-bold mb-4">{plan.name}</h3>
            <div className="text-4xl font-extrabold mb-6">{plan.price}</div>
            <ul className="space-y-3 mb-8">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-center gap-2">
                  <CheckCircle className={`w-5 h-5 ${plan.popular ? 'text-gray-300' : 'text-gray-600'}`} />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <button className={`w-full py-3 rounded-xl font-bold transition-all duration-300 ${plan.popular ? 'bg-white text-gray-900 hover:bg-gray-100' : 'bg-gray-800 text-white hover:bg-gray-900'}`}>
              立即购买
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const Slide10 = () => (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <div className="text-center max-w-3xl">
        <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gray-800 to-gray-900 mb-8">
          开始您的英语学习之旅
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          立即体验AI智能学习助手，让学习更高效、更有趣！
        </p>
        
        <div className="flex gap-6 justify-center mb-12">
          <a href="https://www.coze.cn/s/llxv2V1cxnQ/" target="_blank" rel="noopener noreferrer" className="px-12 py-4 bg-gradient-to-r from-gray-600 to-gray-800 text-white text-xl font-bold rounded-2xl hover:shadow-xl transition-all duration-300 hover:scale-105">
            少儿英语智能体
          </a>
          <a href="https://www.coze.cn/s/i-ipKPU1uDk/" target="_blank" rel="noopener noreferrer" className="px-12 py-4 bg-gradient-to-r from-gray-700 to-gray-900 text-white text-xl font-bold rounded-2xl hover:shadow-xl transition-all duration-300 hover:scale-105">
            口译训练智能体
          </a>
        </div>
        
        <div className="text-gray-500">
          <p className="mb-2">扫描二维码关注我们</p>
          <div className="w-40 h-40 bg-gray-100 rounded-2xl mx-auto flex items-center justify-center border-2 border-gray-300">
            <span className="text-gray-400 text-sm">二维码占位</span>
          </div>
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
            className="absolute left-8 top-1/2 -translate-y-1/2 w-14 h-14 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 hover:scale-110 transition-all duration-300 z-20 border border-gray-200"
          >
            <ChevronLeft className="w-7 h-7 text-gray-700" />
          </button>
        )}
        
        {currentSlide < slides.length - 1 && (
          <button
            onClick={nextSlide}
            className="absolute right-8 top-1/2 -translate-y-1/2 w-14 h-14 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 hover:scale-110 transition-all duration-300 z-20 border border-gray-200"
          >
            <ChevronRight className="w-7 h-7 text-gray-700" />
          </button>
        )}
        
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${index === currentSlide ? 'bg-gradient-to-r from-gray-600 to-gray-800 w-10' : 'bg-gray-300 hover:bg-gray-400'}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
