import React from 'react';

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  created_at: string;
  document_count: number;
}

interface KnowledgeBaseProps {
  knowledgeBases: KnowledgeBase[];
}

const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({ knowledgeBases }) => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">知识库管理</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {knowledgeBases.map((kb) => (
          <div key={kb.id} className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-2">{kb.name}</h2>
            <p className="text-gray-600 mb-4">{kb.description}</p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>创建时间: {kb.created_at}</span>
              <span>文档数: {kb.document_count}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeBase; 