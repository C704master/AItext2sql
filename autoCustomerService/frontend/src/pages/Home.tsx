import { Link } from 'react-router-dom'

const features = [
  {
    name: '智能客服',
    description: '基于大语言模型的智能客服系统，可以回答用户问题并提供专业服务。',
    href: '/customer-service',
  },
  {
    name: '数据分析',
    description: '将自然语言转换为SQL查询，并提供数据可视化分析。',
    href: '/text2sql',
  },
  {
    name: '知识库',
    description: '基于RAG技术的知识库问答系统，提供精确的知识检索。',
    href: '/knowledge-base',
  },
  {
    name: '文档创作',
    description: '智能文档创作助手，根据模板和参数生成专业文档。',
    href: '/document-creation',
  },
]

export default function Home() {
  return (
    <div className="bg-white">
      <div className="mx-auto max-w-7xl py-16 px-4 sm:py-24 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
            <span className="block">华侨大学智能体综合应用平台</span>
          </h1>
          <p className="mx-auto mt-3 max-w-md text-base text-gray-500 sm:text-lg md:mt-5 md:max-w-3xl md:text-xl">
            基于大语言模型的智能体综合应用平台，提供多种智能服务，助力教学科研。
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mt-12">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div
                key={feature.name}
                className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400 hover:ring-1 hover:ring-gray-400"
              >
                <div className="flex h-full flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {feature.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      {feature.description}
                    </p>
                  </div>
                  <div className="mt-4">
                    <Link
                      to={feature.href}
                      className="text-sm font-medium text-primary-600 hover:text-primary-500"
                    >
                      开始使用
                      <span aria-hidden="true"> &rarr;</span>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 