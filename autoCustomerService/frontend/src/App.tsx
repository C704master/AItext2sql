import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Login from './pages/Login';
import Layout from './components/Layout';
import KnowledgeBase from './pages/KnowledgeBase';
import Chat from './pages/Chat';
import Text2SQL from './pages/Text2SQL';
import DocumentCreation from './pages/DocumentCreation';

// 模拟数据
const mockKnowledgeBases = [
  {
    id: 1,
    name: '产品知识库',
    description: '包含所有产品相关信息',
    created_at: '2024-01-01',
    document_count: 10
  },
  {
    id: 2,
    name: '技术支持库',
    description: '常见问题解答和技术支持文档',
    created_at: '2024-01-02',
    document_count: 15
  }
];

const mockChatHistory = [
  {
    id: 1,
    role: 'user',
    content: '你好，我想了解产品A的详细信息',
    timestamp: '2024-03-20T10:00:00Z'
  },
  {
    id: 2,
    role: 'assistant',
    content: '您好！产品A是我们最新推出的智能客服解决方案，具有以下特点：\n\n1. 自然语言处理能力\n2. 多轮对话支持\n3. 知识库集成\n4. 数据分析功能\n\n您想了解哪个方面的具体信息呢？',
    timestamp: '2024-03-20T10:01:00Z'
  },
  {
    id: 3,
    role: 'user',
    content: '它的价格是多少？',
    timestamp: '2024-03-20T10:02:00Z'
  },
  {
    id: 4,
    role: 'assistant',
    content: '产品A的价格根据企业规模和功能需求有所不同：\n\n- 基础版：¥999/月\n- 专业版：¥1999/月\n- 企业版：¥3999/月\n\n所有版本都包含7天免费试用期。您需要我为您详细介绍各个版本的功能区别吗？',
    timestamp: '2024-03-20T10:03:00Z'
  }
];

const mockSQLResult = {
  sql: 'SELECT * FROM users WHERE status = "active"',
  explanation: '查询所有状态为活跃的用户',
  results: [
    { id: 1, username: 'user1', status: 'active' },
    { id: 2, username: 'user2', status: 'active' }
  ]
};

const mockDocument = {
  title: '产品使用指南',
  content: '欢迎使用我们的产品...',
  category: '用户手册'
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true); // 设置为 true 以直接进入主界面

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
        {isAuthenticated ? (
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/knowledge" replace />} />
            <Route path="/knowledge" element={<KnowledgeBase knowledgeBases={mockKnowledgeBases} />} />
            <Route path="/chat" element={<Chat chatHistory={mockChatHistory} />} />
            <Route path="/text2sql" element={<Text2SQL initialResult={mockSQLResult} />} />
            <Route path="/document" element={<DocumentCreation initialDocument={mockDocument} />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  );
}

export default App; 