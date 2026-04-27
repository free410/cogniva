'use client'

import { Layout } from '@/components'
import { DocumentList } from '@/components/documents'
import { FileText } from 'lucide-react'
import { PageHeader } from '@/components/layout'

export default function DocumentsPage() {
  return (
    <Layout>
      <div className="h-full flex flex-col">
        <PageHeader
          icon={<FileText className="w-6 h-6" style={{ color: '#92703a' }} />}
          title="知识库"
          subtitle="文档管理与检索增强生成"
        />

        {/* 内容区域 */}
        <div className="flex-1 overflow-hidden p-6">
          <DocumentList />
        </div>
      </div>
    </Layout>
  )
}
