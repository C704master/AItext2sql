import React from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

interface SQLResult {
  sql: string
  explanation: string
  results: Array<Record<string, any>>
}

interface Text2SQLProps {
  initialResult?: SQLResult
}

const Text2SQL: React.FC<Text2SQLProps> = ({ initialResult }) => {
  const [result, setResult] = React.useState<SQLResult | null>(initialResult || null)
  const [question, setQuestion] = React.useState('')
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    // 这里添加实际的 API 调用
    setLoading(false)
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Text2SQL 转换</h1>
      
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-4">
          <label htmlFor="question" className="block text-gray-700 font-medium mb-2">
            输入问题
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full p-2 border rounded-md"
            rows={4}
            placeholder="请输入您的问题..."
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? '处理中...' : '转换'}
        </button>
      </form>

      {result && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2">生成的 SQL 语句</h2>
            <SyntaxHighlighter language="sql" style={tomorrow}>
              {result.sql}
            </SyntaxHighlighter>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">解释</h2>
            <p className="text-gray-700">{result.explanation}</p>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">查询结果</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white">
                <thead>
                  <tr>
                    {Object.keys(result.results[0] || {}).map((key) => (
                      <th key={key} className="px-4 py-2 border">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.results.map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((value, i) => (
                        <td key={i} className="px-4 py-2 border">
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Text2SQL 