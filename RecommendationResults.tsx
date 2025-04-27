'use client';

import React, { useState } from 'react';
import { useHealth } from '../context/HealthContext';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

const RecommendationResults: React.FC = () => {
  const { healthData, recommendations, setRecommendations, prevStep, email, setEmail } = useHealth();
  const [loading, setLoading] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  
  // 模擬從後端獲取推薦結果
  React.useEffect(() => {
    if (!recommendations) {
      generateRecommendations();
    }
  }, []);
  
  const generateRecommendations = async () => {
    setLoading(true);
    try {
      // 在實際應用中，這裡會調用後端API來生成推薦
      // 現在我們模擬一些基於用戶選擇的推薦
      
      // 等待1秒模擬API調用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 根據用戶的症狀、身體系統問題和特定狀況生成推薦
      const recommendedSupplements: string[] = [];
      const dosage: Record<string, string> = {};
      const usage: Record<string, string> = {};
      let explanation = '';
      
      // 處理症狀
      if (healthData.symptoms.includes('失眠')) {
        recommendedSupplements.push('強鈣配方');
        recommendedSupplements.push('B群');
        dosage['強鈣配方'] = '每日1-2次，每次1片';
        usage['強鈣配方'] = '飯後服用，避免與茶、咖啡同時服用';
        dosage['B群'] = '每日1次，每次1片';
        usage['B群'] = '早餐後服用，增加能量代謝';
      }
      
      if (healthData.symptoms.includes('疼痛')) {
        if (!recommendedSupplements.includes('強鈣配方')) {
          recommendedSupplements.push('強鈣配方');
          dosage['強鈣配方'] = '每日1-2次，每次1片';
          usage['強鈣配方'] = '飯後服用，避免與茶、咖啡同時服用';
        }
        recommendedSupplements.push('蘆薈汁');
        dosage['蘆薈汁'] = '每日2-3次，每次30ml';
        usage['蘆薈汁'] = '稀釋後飲用，可緩解發炎症狀';
      }
      
      if (healthData.symptoms.includes('胃部不適')) {
        recommendedSupplements.push('蘆薈汁');
        recommendedSupplements.push('消化酵素');
        if (!dosage['蘆薈汁']) {
          dosage['蘆薈汁'] = '每日2-3次，每次30ml';
          usage['蘆薈汁'] = '稀釋後飲用，可緩解發炎症狀';
        }
        dosage['消化酵素'] = '每餐前服用，每次1-2粒';
        usage['消化酵素'] = '餐前15-30分鐘服用，幫助消化';
      }
      
      // 處理身體系統問題
      if (healthData.bodySystemIssues.includes('神經系統')) {
        if (!recommendedSupplements.includes('B群')) {
          recommendedSupplements.push('B群');
          dosage['B群'] = '每日1次，每次1片';
          usage['B群'] = '早餐後服用，增加能量代謝';
        }
        recommendedSupplements.push('魚油');
        dosage['魚油'] = '每日1次，每次1-2粒';
        usage['魚油'] = '餐後服用，幫助吸收';
      }
      
      if (healthData.bodySystemIssues.includes('免疫系統')) {
        recommendedSupplements.push('OPC3');
        dosage['OPC3'] = '每日1次，每次1匙';
        usage['OPC3'] = '早上空腹服用，用30ml水調勻';
      }
      
      // 處理特定身體狀況
      if (healthData.specificConditions.includes('乾眼症')) {
        if (!recommendedSupplements.includes('OPC3')) {
          recommendedSupplements.push('OPC3');
          dosage['OPC3'] = '每日1次，每次1匙';
          usage['OPC3'] = '早上空腹服用，用30ml水調勻';
        }
        recommendedSupplements.push('適明（葉黃素）');
        dosage['適明（葉黃素）'] = '每日1次，每次1粒';
        usage['適明（葉黃素）'] = '餐後服用，保護視力';
      }
      
      if (healthData.specificConditions.includes('過敏性鼻炎')) {
        if (!recommendedSupplements.includes('OPC3')) {
          recommendedSupplements.push('OPC3');
          dosage['OPC3'] = '每日1次，每次1匙';
          usage['OPC3'] = '早上空腹服用，用30ml水調勻';
        }
        if (!recommendedSupplements.includes('魚油')) {
          recommendedSupplements.push('魚油');
          dosage['魚油'] = '每日1次，每次1-2粒';
          usage['魚油'] = '餐後服用，幫助吸收';
        }
      }
      
      // 如果沒有足夠的推薦，添加一些基本保健品
      if (recommendedSupplements.length < 2) {
        recommendedSupplements.push('綜合維他命');
        dosage['綜合維他命'] = '每日1次，每次1片';
        usage['綜合維他命'] = '早餐後服用，補充基本營養';
      }
      
      // 生成解釋文本
      explanation = `根據您提供的健康信息，我們為您推薦了${recommendedSupplements.length}種保健品。這些保健品針對您的${healthData.symptoms.join('、')}等症狀，以及${healthData.bodySystemIssues.join('、')}等身體系統需求進行了優化選擇。堅持使用這些保健品，配合均衡飲食和適當運動，有助於改善您的整體健康狀況。建議您在一個季度（約3個月）後進行健康重新評估，以調整保健方案。`;
      
      // 設置推薦結果
      setRecommendations({
        supplements: recommendedSupplements,
        dosage,
        usage,
        explanation
      });
    } catch (error) {
      console.error('生成推薦時出錯:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleGeneratePDF = async () => {
    setGeneratingPdf(true);
    const reportElement = document.getElementById('recommendation-report');
    
    if (reportElement) {
      try {
        const canvas = await html2canvas(reportElement, { scale: 2 });
        const imgData = canvas.toDataURL('image/png');
        
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
        const imgX = (pdfWidth - imgWidth * ratio) / 2;
        const imgY = 30;
        
        pdf.setFontSize(20);
        pdf.text('健康評估與保健品推薦報告', pdfWidth / 2, 20, { align: 'center' });
        
        pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
        pdf.save('健康評估報告.pdf');
      } catch (error) {
        console.error('生成PDF時出錯:', error);
      }
    }
    setGeneratingPdf(false);
  };
  
  const handleSendEmail = async () => {
    if (!email) return;
    
    try {
      // 在實際應用中，這裡會調用後端API來發送郵件
      // 現在我們只是模擬發送成功
      await new Promise(resolve => setTimeout(resolve, 1000));
      setEmailSent(true);
    } catch (error) {
      console.error('發送郵件時出錯:', error);
    }
  };
  
  if (loading || !recommendations) {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">生成個人化推薦中...</h2>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">您的個人化保健品推薦</h2>
      
      <div id="recommendation-report" className="space-y-6">
        {/* 健康評估摘要 */}
        <div className="bg-blue-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">健康評估摘要</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">基本信息</p>
              <p className="text-gray-700">
                {healthData.basicInfo.gender === 'male' ? '男' : healthData.basicInfo.gender === 'female' ? '女' : '其他'}性，
                {healthData.basicInfo.age}歲，
                身高{healthData.basicInfo.height}cm，
                體重{healthData.basicInfo.weight}kg
              </p>
            </div>
            
            {healthData.symptoms.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-500">主要症狀</p>
                <p className="text-gray-700">{healthData.symptoms.join('、')}</p>
              </div>
            )}
            
            {healthData.bodySystemIssues.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-500">需要支持的身體系統</p>
                <p className="text-gray-700">{healthData.bodySystemIssues.join('、')}</p>
              </div>
            )}
            
            {healthData.specificConditions.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-500">特定身體狀況</p>
                <p className="text-gray-700">{healthData.specificConditions.join('、')}</p>
              </div>
            )}
          </div>
        </div>
        
        {/* 推薦解釋 */}
        <div className="bg-green-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold text-green-800 mb-2">推薦說明</h3>
          <p className="text-green-700">{recommendations.explanation}</p>
        </div>
        
        {/* 推薦保健品列表 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold mb-4">推薦保健品</h3>
          <div className="space-y-4">
            {recommendations.supplements.map((supplement, index) => (
              <div key={index} className="border-b pb-3">
                <div className="flex justify-between items-start">
                  <h4 className="text-md font-medium text-blue-700">{supplement}</h4>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                    推薦指數: {5 - index > 0 ? '⭐'.repeat(5 - index) : '⭐'}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div>
                    <p className="text-sm font-medium text-gray-500">建議劑量</p>
                    <p className="text-gray-700">{recommendations.dosage[supplement]}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">使用方法</p>
                    <p className="text-gray-700">{recommendations.usage[supplement]}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* 使用建議 */}
        <div className="bg-yellow-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">使用建議</h3>
          <ul className="list-disc pl-5 space-y-1 text-yellow-700">
            <li>保健品應作為均衡飲食的補充，不能替代正常飲食</li>
            <li>請按照建議劑量服用，不要過量</li>
            <li>如有慢性疾病或正在服用藥物，請在服用前諮詢醫生</li>
            <li>保持規律作息和適當運動，效果更佳</li>
            <li>建議在3個月後重新評估健康狀況，調整保健方案</li>
          </ul>
        </div>
      </div>
      
      {/* 操作按鈕 */}
      <div className="mt-8 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <button
            onClick={prevStep}
            className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            返回AI評估
          </button>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <button
              onClick={handleGeneratePDF}
              disabled={generatingPdf}
              className={`px-4 py-2 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                generatingPdf 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {generatingPdf ? '生成中...' : '下載PDF報告'}
            </button>
            
            <button
              onClick={() => setShowEmailForm(true)}
              className="px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              通過Email接收報告
            </button>
          </div>
        </div>
        
        {/* Email表單 */}
        {showEmailForm && (
          <div className="mt-4 p-4 border border-gray-200 rounded-md">
            <h3 className="text-lg font-semibold mb-3">接收完整報告</h3>
            {emailSent ? (
              <div className="bg-green-50 p-3 rounded-md text-green-700">
                報告已成功發送到您的郵箱！請查收。
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="請輸入您的Email地址"
                  className="flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSendEmail}
                  disabled={!email}
                  className={`px-4 py-2 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    email 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  發送報告
                </button>
              </div>
            )}
            <p className="mt-2 text-sm text-gray-500">
              我們將發送完整的健康評估報告到您的郵箱，包含更詳細的保健建議和使用指南。
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationResults;
