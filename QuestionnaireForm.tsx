'use client';

import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useHealth } from '../context/HealthContext';

// 定義問卷表單類型
type QuestionnaireInputs = {
  age: string;
  gender: string;
  height: string;
  weight: string;
  symptoms: string[];
  bodySystemIssues: string[];
  specificConditions: string[];
};

const QuestionnaireForm: React.FC = () => {
  const { updateHealthData, nextStep } = useHealth();
  const { register, handleSubmit, formState: { errors } } = useForm<QuestionnaireInputs>();
  
  // 症狀選項
  const symptomOptions = [
    '失眠', '疼痛', '胃部不適', '腹瀉', '發炎'
  ];
  
  // 身體系統選項
  const bodySystemOptions = [
    '神經系統', '呼吸系統', '消化系統', '骨骼系統', '免疫系統', '心血管系統', '內分泌系統'
  ];
  
  // 特定身體狀況選項
  const specificConditionOptions = [
    '白髮', '掉髮', '長時間使用電腦', '乾眼症', '黑眼圈', '氣喘', '鼻竇炎', 
    '慢性支氣管炎', '過敏性鼻炎', '牙周病', '口腔潰瘍', '蛀牙', '嘴破', '動脈硬化', '糖尿病'
  ];
  
  // 選中的選項狀態
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [selectedBodySystems, setSelectedBodySystems] = useState<string[]>([]);
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  
  // 處理症狀選擇
  const handleSymptomChange = (symptom: string) => {
    setSelectedSymptoms(prev => 
      prev.includes(symptom) 
        ? prev.filter(s => s !== symptom) 
        : [...prev, symptom]
    );
  };
  
  // 處理身體系統選擇
  const handleBodySystemChange = (system: string) => {
    setSelectedBodySystems(prev => 
      prev.includes(system) 
        ? prev.filter(s => s !== system) 
        : [...prev, system]
    );
  };
  
  // 處理特定狀況選擇
  const handleConditionChange = (condition: string) => {
    setSelectedConditions(prev => 
      prev.includes(condition) 
        ? prev.filter(c => c !== condition) 
        : [...prev, condition]
    );
  };
  
  // 表單提交處理
  const onSubmit: SubmitHandler<QuestionnaireInputs> = (data) => {
    // 更新健康數據上下文
    updateHealthData({
      basicInfo: {
        age: data.age,
        gender: data.gender,
        height: data.height,
        weight: data.weight
      },
      symptoms: selectedSymptoms,
      bodySystemIssues: selectedBodySystems,
      specificConditions: selectedConditions
    });
    
    // 進入下一步
    nextStep();
  };
  
  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">健康問卷</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* 基本信息區塊 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold mb-4">基本信息</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">年齡</label>
              <input
                type="number"
                {...register('age', { required: '請輸入年齡' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.age && <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">性別</label>
              <select
                {...register('gender', { required: '請選擇性別' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">請選擇</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
              {errors.gender && <p className="text-red-500 text-sm mt-1">{errors.gender.message}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">身高 (cm)</label>
              <input
                type="number"
                {...register('height', { required: '請輸入身高' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.height && <p className="text-red-500 text-sm mt-1">{errors.height.message}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">體重 (kg)</label>
              <input
                type="number"
                {...register('weight', { required: '請輸入體重' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.weight && <p className="text-red-500 text-sm mt-1">{errors.weight.message}</p>}
            </div>
          </div>
        </div>
        
        {/* 症狀選擇區塊 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold mb-4">您目前有哪些症狀？（可多選）</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {symptomOptions.map((symptom) => (
              <div key={symptom} className="flex items-center">
                <input
                  type="checkbox"
                  id={`symptom-${symptom}`}
                  checked={selectedSymptoms.includes(symptom)}
                  onChange={() => handleSymptomChange(symptom)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`symptom-${symptom}`} className="ml-2 block text-sm text-gray-700">
                  {symptom}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* 身體系統問題區塊 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold mb-4">您的哪些身體系統需要支持？（可多選）</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {bodySystemOptions.map((system) => (
              <div key={system} className="flex items-center">
                <input
                  type="checkbox"
                  id={`system-${system}`}
                  checked={selectedBodySystems.includes(system)}
                  onChange={() => handleBodySystemChange(system)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`system-${system}`} className="ml-2 block text-sm text-gray-700">
                  {system}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* 特定身體狀況區塊 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-semibold mb-4">您有以下哪些特定身體狀況？（可多選）</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {specificConditionOptions.map((condition) => (
              <div key={condition} className="flex items-center">
                <input
                  type="checkbox"
                  id={`condition-${condition}`}
                  checked={selectedConditions.includes(condition)}
                  onChange={() => handleConditionChange(condition)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`condition-${condition}`} className="ml-2 block text-sm text-gray-700">
                  {condition}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* 提交按鈕 */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            下一步：AI深度評估
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuestionnaireForm;
