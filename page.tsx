'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SettingsPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [settings, setSettings] = useState({
    apiBaseUrl: '',
    productApiBaseUrl: '',
    reminderApiBaseUrl: '',
    gmailUser: '',
    gmailPassword: '',
    openaiApiKey: ''
  });
  const router = useRouter();

  // 檢查是否已登入
  useEffect(() => {
    const adminToken = localStorage.getItem('adminToken');
    if (adminToken) {
      setIsLoggedIn(true);
      loadSettings();
    } else {
      router.push('/admin');
    }
  }, [router]);

  // 從localStorage載入設置
  const loadSettings = () => {
    setSettings({
      apiBaseUrl: localStorage.getItem('apiBaseUrl') || '',
      productApiBaseUrl: localStorage.getItem('productApiBaseUrl') || '',
      reminderApiBaseUrl: localStorage.getItem('reminderApiBaseUrl') || '',
      gmailUser: localStorage.getItem('gmailUser') || '',
      gmailPassword: localStorage.getItem('gmailPassword') || '',
      openaiApiKey: localStorage.getItem('openaiApiKey') || ''
    });
  };

  // 保存設置到localStorage
  const saveSettings = () => {
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      // 保存API端點設置
      if (settings.apiBaseUrl) {
        localStorage.setItem('apiBaseUrl', settings.apiBaseUrl);
      } else {
        localStorage.removeItem('apiBaseUrl');
      }

      if (settings.productApiBaseUrl) {
        localStorage.setItem('productApiBaseUrl', settings.productApiBaseUrl);
      } else {
        localStorage.removeItem('productApiBaseUrl');
      }

      if (settings.reminderApiBaseUrl) {
        localStorage.setItem('reminderApiBaseUrl', settings.reminderApiBaseUrl);
      } else {
        localStorage.removeItem('reminderApiBaseUrl');
      }

      // 保存Gmail設置
      if (settings.gmailUser) {
        localStorage.setItem('gmailUser', settings.gmailUser);
      } else {
        localStorage.removeItem('gmailUser');
      }

      if (settings.gmailPassword) {
        localStorage.setItem('gmailPassword', settings.gmailPassword);
      } else {
        localStorage.removeItem('gmailPassword');
      }

      // 保存OpenAI設置
      if (settings.openaiApiKey) {
        localStorage.setItem('openaiApiKey', settings.openaiApiKey);
      } else {
        localStorage.removeItem('openaiApiKey');
      }

      setSuccessMessage('設置已保存');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('保存設置錯誤:', err);
      setError('保存設置時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 測試API連接
  const testApiConnection = async () => {
    if (!settings.apiBaseUrl) {
      setError('請先設置主要API端點');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch(`${settings.apiBaseUrl}/`);
      
      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(`API連接成功: ${JSON.stringify(data)}`);
        setTimeout(() => setSuccessMessage(''), 5000);
      } else {
        setError(`API連接失敗: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('API連接錯誤:', err);
      setError(`API連接錯誤: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 測試產品API連接
  const testProductApiConnection = async () => {
    if (!settings.productApiBaseUrl) {
      setError('請先設置產品管理API端點');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch(`${settings.productApiBaseUrl}/`);
      
      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(`產品API連接成功: ${JSON.stringify(data)}`);
        setTimeout(() => setSuccessMessage(''), 5000);
      } else {
        setError(`產品API連接失敗: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('產品API連接錯誤:', err);
      setError(`產品API連接錯誤: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 測試提醒API連接
  const testReminderApiConnection = async () => {
    if (!settings.reminderApiBaseUrl) {
      setError('請先設置提醒系統API端點');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch(`${settings.reminderApiBaseUrl}/`);
      
      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(`提醒API連接成功: ${JSON.stringify(data)}`);
        setTimeout(() => setSuccessMessage(''), 5000);
      } else {
        setError(`提醒API連接失敗: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('提醒API連接錯誤:', err);
      setError(`提醒API連接錯誤: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 保存Gmail設置到後端
  const saveGmailSettings = async () => {
    if (!settings.apiBaseUrl) {
      setError('請先設置主要API端點');
      return;
    }

    if (!settings.gmailUser || !settings.gmailPassword) {
      setError('請填寫Gmail帳號和密碼');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const adminToken = localStorage.getItem('adminToken');
      const response = await fetch(`${settings.apiBaseUrl}/api/admin/settings/email`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          gmail_user: settings.gmailUser,
          gmail_password: settings.gmailPassword
        })
      });
      
      if (response.ok) {
        setSuccessMessage('Gmail設置已保存到後端');
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        const errorText = await response.text();
        setError(`保存Gmail設置失敗: ${errorText}`);
      }
    } catch (err) {
      console.error('保存Gmail設置錯誤:', err);
      setError(`保存Gmail設置錯誤: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 保存OpenAI設置到後端
  const saveOpenAISettings = async () => {
    if (!settings.apiBaseUrl) {
      setError('請先設置主要API端點');
      return;
    }

    if (!settings.openaiApiKey) {
      setError('請填寫OpenAI API密鑰');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const adminToken = localStorage.getItem('adminToken');
      const response = await fetch(`${settings.apiBaseUrl}/api/admin/settings/openai`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          api_key: settings.openaiApiKey
        })
      });
      
      if (response.ok) {
        setSuccessMessage('OpenAI設置已保存到後端');
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        const errorText = await response.text();
        setError(`保存OpenAI設置失敗: ${errorText}`);
      }
    } catch (err) {
      console.error('保存OpenAI設置錯誤:', err);
      setError(`保存OpenAI設置錯誤: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 返回管理後台
  const goBackToDashboard = () => {
    router.push('/admin');
  };

  // 自動推斷API端點
  const inferApiEndpoints = () => {
    const currentUrl = window.location.origin;
    const mainApiUrl = currentUrl.replace('3000', '8001');
    const productApiUrl = currentUrl.replace('3000', '8003');
    const reminderApiUrl = currentUrl.replace('3000', '8004');
    
    setSettings({
      ...settings,
      apiBaseUrl: mainApiUrl,
      productApiBaseUrl: productApiUrl,
      reminderApiBaseUrl: reminderApiUrl
    });
  };

  if (!isLoggedIn) {
    return (
      <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <p className="text-center">請先登入管理後台</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto mt-6 p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">系統設置</h1>
        <button
          onClick={goBackToDashboard}
          className="bg-gray-300 text-gray-800 py-1 px-3 rounded hover:bg-gray-400 focus:outline-none focus:bg-gray-400"
        >
          返回管理後台
        </button>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
          {successMessage}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* API端點設置 */}
        <div className="p-4 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">API端點設置</h2>
          
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="apiBaseUrl">
              主要API端點
            </label>
            <input
              id="apiBaseUrl"
              type="text"
              value={settings.apiBaseUrl}
              onChange={(e) => setSettings({...settings, apiBaseUrl: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              placeholder="https://8001-xxxx.manus.computer"
            />
            <p className="text-sm text-gray-500 mt-1">
              用於用戶數據和報告管理的API端點
            </p>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="productApiBaseUrl">
              產品管理API端點
            </label>
            <input
              id="productApiBaseUrl"
              type="text"
              value={settings.productApiBaseUrl}
              onChange={(e) => setSettings({...settings, productApiBaseUrl: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              placeholder="https://8003-xxxx.manus.computer"
            />
            <p className="text-sm text-gray-500 mt-1">
              用於產品管理的API端點
            </p>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="reminderApiBaseUrl">
              提醒系統API端點
            </label>
            <input
              id="reminderApiBaseUrl"
              type="text"
              value={settings.reminderApiBaseUrl}
              onChange={(e) => setSettings({...settings, reminderApiBaseUrl: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              placeholder="https://8004-xxxx.manus.computer"
            />
            <p className="text-sm text-gray-500 mt-1">
              用於二次測試提醒的API端點
            </p>
          </div>
          
          <div className="flex space-x-2 mb-4">
            <button
              onClick={inferApiEndpoints}
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 focus:outline-none focus:bg-gray-600"
              disabled={loading}
            >
              自動推斷端點
            </button>
            
            <button
              onClick={testApiConnection}
              className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:bg-blue-600"
              disabled={loading || !settings.apiBaseUrl}
            >
              測試主API
            </button>
            
            <button
              onClick={testProductApiConnection}
              className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 focus:outline-none focus:bg-green-600"
              disabled={loading || !settings.productApiBaseUrl}
            >
              測試產品API
            </button>
            
            <button
              onClick={testReminderApiConnection}
              className="bg-purple-500 text-white py-2 px-4 rounded hover:bg-purple-600 focus:outline-none focus:bg-purple-600"
              disabled={loading || !settings.reminderApiBaseUrl}
            >
              測試提醒API
            </button>
          </div>
        </div>
        
        {/* 憑證設置 */}
        <div className="p-4 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">API憑證設置</h2>
          
          <div className="mb-4">
            <h3 className="font-semibold mb-2">Gmail設置</h3>
            <div className="mb-2">
              <label className="block text-gray-700 mb-1" htmlFor="gmailUser">
                Gmail帳號
              </label>
              <input
                id="gmailUser"
                type="email"
                value={settings.gmailUser}
                onChange={(e) => setSettings({...settings, gmailUser: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                placeholder="your.email@gmail.com"
              />
            </div>
            
            <div className="mb-2">
              <label className="block text-gray-700 mb-1" htmlFor="gmailPassword">
                Gmail應用密碼
              </label>
              <input
                id="gmailPassword"
                type="password"
                value={settings.gmailPassword}
                onChange={(e) => setSettings({...settings, gmailPassword: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                placeholder="應用密碼（非Gmail登入密碼）"
              />
              <p className="text-sm text-gray-500 mt-1">
                <a 
                  href="https://myaccount.google.com/apppasswords" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  如何獲取應用密碼？
                </a>
              </p>
            </div>
            
            <button
              onClick={saveGmailSettings}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:bg-blue-600 mb-4"
              disabled={loading || !settings.gmailUser || !settings.gmailPassword}
            >
              保存Gmail設置到後端
            </button>
          </div>
          
          <div className="mb-4 border-t pt-4">
            <h3 className="font-semibold mb-2">OpenAI API設置</h3>
            <div className="mb-2">
              <label className="block text-gray-700 mb-1" htmlFor="openaiApiKey">
                OpenAI API密鑰
              </label>
              <input
                id="openaiApiKey"
                type="password"
                value={settings.openaiApiKey}
                onChange={(e) => setSettings({...settings, openaiApiKey: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                placeholder="sk-..."
              />
              <p className="text-sm text-gray-500 mt-1">
                <a 
                  href="https://platform.openai.com/api-keys" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  如何獲取OpenAI API密鑰？
                </a>
              </p>
            </div>
            
            <button
              onClick={saveOpenAISettings}
              className="w-full 
(Content truncated due to size limit. Use line ranges to read in chunks)