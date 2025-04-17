import React from 'react';

interface Document {
  title: string;
  content: string;
  category: string;
}

interface DocumentCreationProps {
  initialDocument?: Document;
}

const DocumentCreation: React.FC<DocumentCreationProps> = ({ initialDocument }) => {
  const [document, setDocument] = React.useState<Document>(
    initialDocument || { title: '', content: '', category: '' }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 这里添加实际的文档保存逻辑
    console.log('保存文档:', document);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">文档创作</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="title" className="block text-gray-700 font-medium mb-2">
            标题
          </label>
          <input
            type="text"
            id="title"
            value={document.title}
            onChange={(e) => setDocument({ ...document, title: e.target.value })}
            className="w-full p-2 border rounded-md"
            placeholder="请输入文档标题"
          />
        </div>

        <div>
          <label htmlFor="category" className="block text-gray-700 font-medium mb-2">
            分类
          </label>
          <input
            type="text"
            id="category"
            value={document.category}
            onChange={(e) => setDocument({ ...document, category: e.target.value })}
            className="w-full p-2 border rounded-md"
            placeholder="请输入文档分类"
          />
        </div>

        <div>
          <label htmlFor="content" className="block text-gray-700 font-medium mb-2">
            内容
          </label>
          <textarea
            id="content"
            value={document.content}
            onChange={(e) => setDocument({ ...document, content: e.target.value })}
            className="w-full p-2 border rounded-md"
            rows={10}
            placeholder="请输入文档内容"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          保存文档
        </button>
      </form>
    </div>
  );
};

export default DocumentCreation; 