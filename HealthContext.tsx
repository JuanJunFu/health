'use client';

import React, { createContext, useState, useContext, ReactNode } from 'react';

// 定義類型
type HealthData = {
  basicInfo: {
    age: string;
    gender: string;
    height: string;
    weight: string;
  };
  symptoms: string[];
  bodySystemIssues: string[];
  specificConditions: string[];
  aiAnswers: Record<string, string>;
};

type RecommendationData = {
  supplements: string[];
  dosage: Record<string, string>;
  usage: Record<string, string>;
  explanation: string;
};

interface HealthContextType {
  healthData: HealthData;
  recommendations: RecommendationData | null;
  currentStep: number;
  updateHealthData: (data: Partial<HealthData>) => void;
  setRecommendations: (data: RecommendationData) => void;
  nextStep: () => void;
  prevStep: () => void;
  resetForm: () => void;
  email: string;
  setEmail: (email: string) => void;
}

// 創建上下文
const HealthContext = createContext<HealthContextType | undefined>(undefined);

// 初始狀態
const initialHealthData: HealthData = {
  basicInfo: {
    age: '',
    gender: '',
    height: '',
    weight: '',
  },
  symptoms: [],
  bodySystemIssues: [],
  specificConditions: [],
  aiAnswers: {},
};

// 提供者組件
export const HealthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [healthData, setHealthData] = useState<HealthData>(initialHealthData);
  const [recommendations, setRecommendations] = useState<RecommendationData | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [email, setEmail] = useState('');

  const updateHealthData = (data: Partial<HealthData>) => {
    setHealthData(prev => ({ ...prev, ...data }));
  };

  const nextStep = () => {
    setCurrentStep(prev => prev + 1);
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(1, prev - 1));
  };

  const resetForm = () => {
    setHealthData(initialHealthData);
    setRecommendations(null);
    setCurrentStep(1);
    setEmail('');
  };

  return (
    <HealthContext.Provider
      value={{
        healthData,
        recommendations,
        currentStep,
        updateHealthData,
        setRecommendations,
        nextStep,
        prevStep,
        resetForm,
        email,
        setEmail
      }}
    >
      {children}
    </HealthContext.Provider>
  );
};

// 自定義鉤子
export const useHealth = () => {
  const context = useContext(HealthContext);
  if (context === undefined) {
    throw new Error('useHealth must be used within a HealthProvider');
  }
  return context;
};
