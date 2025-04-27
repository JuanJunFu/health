'use client';

import React, { useState, useEffect } from 'react';
import { useHealth } from '../context/HealthContext';

const AiQuestionnaire: React.FC = () => {
  const { healthData, updateHealthData, nextStep, prevStep } = useHealth();
  const [loading, setLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [aiQuestions, setAiQuestions] = useState<string[]>([]);
  const [aiAnswers, setAiAnswers] = useState<Record<string, string>>({});
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // 根據用戶的基本問卷回答生成AI問題
  useEffect(() => {
    generateInitialQuestions();
  }, []);

  const generateInitialQuestions = async () => {
    setLoading(true);
    try {
      // 在實際應用中，這裡會調用後端API來生成問題
      // 現在我們模擬一些基於用戶選擇的問題
      const questions: string[] = [];
      
      // 基於症狀生成問題
      if (healthData.symptoms.includes('失眠')) {
        questions.push('您的失眠情況持續多久了？是否有特定時間段特別嚴重？');
      }
      
      if (healthData.symptoms.includes('疼痛')) {
        questions.push('您的疼痛主要集中在哪些部位？疼痛的性質是怎樣的（如：刺痛、鈍痛、灼熱感等）？');
      }
      
      if (healthData.symptoms.includes('胃部不適')) {
        questions.push('您的胃部不適通常在什麼時候發生？是否與進食有關？');
      }
      
      // 基於身體系統問題生成問題
      if (healthData.bodySystemIssues.includes('神經系統')) {
        questions.push('您是否經常感到頭痛、頭暈或注意力不集中？這些症狀多久出現一次？');
      }
      
      if (healthData.bodySystemIssues.includes('消化系統')) {
        questions.push('您的消化問題主要表現為哪些症狀？是否有食物不耐受的情況？');
      }
      
      // 基於特定身體狀況生成問題
      if (healthData.specificConditions.includes('乾眼症')) {
        questions.push('您的乾眼症狀是否與用眼時間或環境因素有關？您目前使用眼藥水嗎？');
      }
      
      if (healthData.specificConditions.includes('過敏性鼻炎')) {
        questions.push('您的過敏症狀是季節性的還是全年都有？已知的過敏原有哪些？');
      }
      
      // 如果沒有足夠的問題，添加一些通用問題
      if (questions.length < 3) {
        questions.push('您平時的飲食習慣如何？是否有特定的飲食偏好或限制？');
        questions.push('您每週的運動頻率和強度如何？');
        questions.push('您的睡眠質量如何？平均每晚睡幾個小時？');
      }
      
      // 最多選擇5個問題
      const selectedQuestions = questions.slice(0, 5);
      setAiQuestions(selectedQuestions);
      
      if (selectedQuestions.length > 0) {
        setCurrentQuestion(selectedQuestions[0]);
      }
    } catch (error) {
      console.error('生成問題時出錯:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = () => {
    if (!answer.trim()) return;
    
    // 保存當前問題的回答
    const updatedAnswers = { ...aiAnswers, [currentQuestion]: answer };
    setAiAnswers(updatedAnswers);
    
    // 更新健康數據上下文
    updateHealthData({ aiAnswers: updatedAnswers });
    
    // 清空當前回答
    setAnswer('');
    
    // 移動到下一個問題或完成
    const nextIndex = questionIndex + 1;
    if (nextIndex < aiQuestions.length) {
      setQuestionIndex(nextIndex);
      setCurrentQuestion(aiQuestions[nextIndex]);
    } else {
      setIsComplete(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAnswerSubmit();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">AI深度健康評估</h2>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : isComplete ? (
        <div className="text-center space-y-6">
          <div className="bg-green-50 p-4 rounded-md">
            <h3 className="text-lg font-semibold text-green-800 mb-2">評估完成！</h3>
            <p className="text-green-700">
              感謝您完成AI深度健康評估。我們已收集足夠的信息來為您提供個性化的保健品推薦。
            </p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-lg font-semibold mb-2">您的回答摘要</h3>
            <div className="space-y-3 text-left">
              {Object.entries(aiAnswers).map(([question, answer], index) => (
                <div key={index} className="border-b pb-2">
                  <p className="font-medium text-gray-700">{question}</p>
                  <p className="text-gray-600 mt-1">{answer}</p>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex justify-between">
            <button
              onClick={prevStep}
              className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              返回問卷
            </button>
            <button
              onClick={nextStep}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              查看推薦結果
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-blue-50 p-4 rounded-md">
            <p className="text-blue-700">
              基於您的初步問卷回答，我們的AI系統生成了一些深入的問題，以便更全面地了解您的健康狀況。
              請回答以下問題，幫助我們為您提供最適合的保健品推薦。
            </p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-md">
            <div className="flex items-center mb-2">
              <div className="bg-blue-100 text-blue-800 font-medium px-2 py-1 rounded text-sm">
                問題 {questionIndex + 1}/{aiQuestions.length}
              </div>
            </div>
            <h3 className="text-lg font-semibold mb-3">{currentQuestion}</h3>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="請輸入您的回答..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px]"
            />
          </div>
          
          <div className="flex justify-between">
            <button
              onClick={prevStep}
              className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              返回問卷
            </button>
            <button
              onClick={handleAnswerSubmit}
              disabled={!answer.trim()}
              className={`px-6 py-2 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                answer.trim() 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {questionIndex < aiQuestions.length - 1 ? '下一個問題' : '完成評估'}
            </button>
          </div>
          
          {/* 已回答的問題摘要 */}
          {Object.keys(aiAnswers).length > 0 && (
            <div className="mt-8 border-t pt-4">
              <h4 className="text-md font-medium mb-2">已回答的問題：</h4>
              <div className="space-y-2">
                {Object.entries(aiAnswers).map(([question, answer], index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded-md">
                    <p className="font-medium text-gray-700">{question}</p>
                    <p className="text-gray-600 mt-1">{answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AiQuestionnaire;
