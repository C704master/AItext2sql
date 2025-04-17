import { useState, useRef } from 'react'
import axios from 'axios'

interface UploadResult {
  file_id: string
  file_name: string
  file_size: number
  file_type: string
  upload_time: string
}

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<UploadResult | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('请选择要上传的文件')
      return
    }

    setUploading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      setError('文件上传失败，请稍后重试')
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">文件上传</h2>
        <div className="space-y-4">
          <div>
            <label
              htmlFor="file"
              className="block text-sm font-medium text-gray-700"
            >
              选择文件
            </label>
            <input
              ref={fileInputRef}
              id="file"
              type="file"
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
          </div>

          {file && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                文件名: {file.name}
              </p>
              <p className="text-sm text-gray-600">
                文件大小: {formatFileSize(file.size)}
              </p>
              <p className="text-sm text-gray-600">
                文件类型: {file.type}
              </p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="btn btn-primary"
          >
            {uploading ? '上传中...' : '上传文件'}
          </button>
        </div>
      </div>

      {error && (
        <div className="card bg-red-50 text-red-600">
          {error}
        </div>
      )}

      {result && (
        <div className="card bg-green-50">
          <h3 className="text-lg font-medium text-green-800 mb-2">
            上传成功
          </h3>
          <div className="space-y-2">
            <p className="text-sm text-green-700">
              文件ID: {result.file_id}
            </p>
            <p className="text-sm text-green-700">
              文件名: {result.file_name}
            </p>
            <p className="text-sm text-green-700">
              文件大小: {formatFileSize(result.file_size)}
            </p>
            <p className="text-sm text-green-700">
              文件类型: {result.file_type}
            </p>
            <p className="text-sm text-green-700">
              上传时间: {new Date(result.upload_time).toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  )
} 