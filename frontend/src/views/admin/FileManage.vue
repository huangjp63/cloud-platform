<template>
  <div class="file-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文件列表</span>
          <el-button type="primary" @click="loadFiles" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-table :data="fileList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="username" label="上传用户" width="120" />
        <el-table-column prop="size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handlePreview(row)"
            >
              预览
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :loading="row.deleting"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="文件预览" width="800px" :fullscreen="isFullscreen">
      <div class="preview-container">
        <!-- 图片预览 -->
        <img v-if="isImage" :src="previewUrl" class="preview-image" />
        <!-- 视频预览 -->
        <video v-else-if="isVideo" :src="previewUrl" controls class="preview-video"></video>
        <!-- 音频预览 -->
        <audio v-else-if="isAudio" :src="previewUrl" controls class="preview-audio"></audio>
        <!-- 文本预览 -->
        <div v-else-if="isText" class="preview-text">
          <pre>{{ previewContent }}</pre>
        </div>
        <!-- 不支持预览 -->
        <div v-else class="preview-unsupported">
          <el-icon :size="64"><Document /></el-icon>
          <p>该文件类型暂不支持预览</p>
          <el-button type="primary" @click="downloadCurrentFile">下载文件</el-button>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
          <el-button v-if="!isFullscreen" type="primary" @click="isFullscreen = true">全屏</el-button>
          <el-button v-else type="primary" @click="isFullscreen = false">退出全屏</el-button>
          <el-button type="primary" @click="downloadCurrentFile">下载</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getAllFiles, deleteFile } from '@/api/admin'
import { previewFile, downloadFile as downloadFileApi } from '@/api/file'
import { formatFileSize, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Document } from '@element-plus/icons-vue'

const fileList = ref([])
const loading = ref(false)

// 预览相关
const previewDialogVisible = ref(false)
const previewUrl = ref('')
const previewContent = ref('')
const isFullscreen = ref(false)
const currentPreviewFile = ref(null)

// 判断文件类型
const isImage = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.filename?.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
})

const isVideo = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.filename?.split('.').pop()?.toLowerCase()
  return ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'].includes(ext)
})

const isAudio = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.filename?.split('.').pop()?.toLowerCase()
  return ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'].includes(ext)
})

const isText = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.filename?.split('.').pop()?.toLowerCase()
  return ['txt', 'md', 'json', 'js', 'html', 'css', 'py', 'java', 'c', 'cpp', 'h', 'xml', 'yaml', 'yml', 'log'].includes(ext)
})

const loadFiles = async () => {
  loading.value = true
  try {
    const res = await getAllFiles()
    fileList.value = res.data.map(file => ({
      ...file,
      deleting: false
    }))
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handlePreview = async (row) => {
  try {
    currentPreviewFile.value = row
    const response = await previewFile(row.id)
    
    if (response.data && response.data.url) {
      // 将 MinIO 内部 URL 转换为通过 Nginx 代理的 URL
      previewUrl.value = response.data.url.replace('http://minio:9000/', 'http://localhost/minio/')
      
      // 对于文本文件，直接获取内容并显示
      if (isText.value) {
        try {
          const textResponse = await fetch(previewUrl.value)
          const textContent = await textResponse.text()
          previewContent.value = textContent
        } catch (error) {
          console.error('获取文本内容失败:', error)
          previewContent.value = '获取文本内容失败，请尝试下载查看'
        }
      } else {
        previewContent.value = ''
      }
      
      previewDialogVisible.value = true
      isFullscreen.value = false
    } else {
      ElMessage.error('获取预览链接失败')
    }
  } catch (error) {
    ElMessage.error('预览失败：' + (error.message || '未知错误'))
  }
}

const downloadCurrentFile = async () => {
  if (currentPreviewFile.value) {
    try {
      const response = await downloadFileApi(currentPreviewFile.value.id)
      const url = window.URL.createObjectURL(new Blob([response]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', currentPreviewFile.value.filename)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      ElMessage.error('下载失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${row.filename}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    row.deleting = true
    await deleteFile(row.id)
    ElMessage.success('删除成功')
    await loadFiles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    row.deleting = false
  }
}

loadFiles()
</script>

<style scoped>
.file-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-container {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
}

.preview-video {
  max-width: 100%;
  max-height: 600px;
}

.preview-audio {
  width: 100%;
}

.preview-text {
  width: 100%;
  max-height: 600px;
  overflow: auto;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 4px;
}

.preview-text pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.preview-unsupported {
  text-align: center;
  color: #909399;
}

.preview-unsupported p {
  margin: 20px 0;
  font-size: 16px;
}
</style>

