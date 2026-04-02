<template>
  <div class="file-manage">
    <el-card>
      <template #header>
        <div class="header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item @click="goToRoot">全部文件</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(item, index) in breadcrumb" :key="item.id" @click="goToFolder(item.id)">{{ item.name }}</el-breadcrumb-item>
          </el-breadcrumb>
          <div class="actions">
            <el-button type="primary" @click="showUploadDialog">上传文件</el-button>
            <el-button @click="createFolder">新建文件夹</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="combinedList" style="width: 100%">
        <el-table-column prop="name" label="文件名">
          <template #default="{ row }">
            <span v-if="row.type === 'folder'" style="display: flex; align-items: center; gap: 8px; cursor: pointer" @click="enterFolder(row)">
              <el-icon><Folder /></el-icon>
              <span>{{ row.name }}</span>
            </span>
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button v-if="row.type === 'file'" link type="primary" @click="previewFile(row)">预览</el-button>
            <el-button v-if="row.type === 'file'" link type="primary" @click="downloadFile(row)">下载</el-button>
            <el-button link type="primary" @click="renameFile(row)">重命名</el-button>
            <el-button link type="danger" @click="deleteFile(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传文件对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :multiple="true"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">
            支持多文件上传，单个文件大小不超过 10GB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmUpload" :loading="uploadLoading">开始上传</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 新建文件夹对话框 -->
    <el-dialog v-model="folderDialogVisible" title="新建文件夹" width="400px">
      <el-form :model="folderForm" :rules="folderRules" ref="folderFormRef">
        <el-form-item label="文件夹名称" prop="name">
          <el-input v-model="folderForm.name" placeholder="请输入文件夹名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="folderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCreateFolder">创建</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名文件" width="400px">
      <el-form :model="renameForm" :rules="renameRules" ref="renameFormRef">
        <el-form-item label="新名称" prop="name">
          <el-input v-model="renameForm.name" placeholder="请输入新名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
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
import { ref, reactive, onMounted, computed } from 'vue'
import { formatFileSize } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Folder, Document } from '@element-plus/icons-vue'
import * as fileApi from '@/api/file'
import * as folderApi from '@/api/folder'
import SparkMD5 from 'spark-md5'

const fileList = ref([])
const folderList = ref([])
const currentFolderId = ref(0)
const breadcrumb = ref([])

const combinedList = computed(() => {
  const files = fileList.value.map(file => ({ ...file, type: 'file' }))
  const folders = folderList.value.map(folder => ({ ...folder, type: 'folder' }))
  return [...folders, ...files].sort((a, b) => {
    if (a.type !== b.type) {
      return a.type === 'folder' ? -1 : 1
    }
    return new Date(b.create_time) - new Date(a.create_time)
  })
})
const uploadDialogVisible = ref(false)
const folderDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const uploadLoading = ref(false)
const selectedFiles = ref([])
const currentFile = ref(null)

// 预览相关
const previewDialogVisible = ref(false)
const previewUrl = ref('')
const previewContent = ref('')
const isFullscreen = ref(false)
const currentPreviewFile = ref(null)

// 判断文件类型
const isImage = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.name?.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
})

const isVideo = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.name?.split('.').pop()?.toLowerCase()
  return ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'].includes(ext)
})

const isAudio = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.name?.split('.').pop()?.toLowerCase()
  return ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'].includes(ext)
})

const isText = computed(() => {
  if (!currentPreviewFile.value) return false
  const ext = currentPreviewFile.value.name?.split('.').pop()?.toLowerCase()
  return ['txt', 'md', 'json', 'js', 'html', 'css', 'py', 'java', 'c', 'cpp', 'h', 'xml', 'yaml', 'yml', 'log'].includes(ext)
})

// 新建文件夹表单
const folderForm = reactive({ name: '' })
const folderFormRef = ref(null)
const folderRules = {
  name: [{ required: true, message: '请输入文件夹名称', trigger: 'blur' }]
}

// 重命名表单
const renameForm = reactive({ name: '' })
const renameFormRef = ref(null)
const renameRules = {
  name: [{ required: true, message: '请输入新名称', trigger: 'blur' }]
}

// 加载文件列表
const loadFileList = async () => {
  try {
    // 调用后端API获取文件列表
    const fileResponse = await fileApi.getFileList(currentFolderId.value)
    fileList.value = fileResponse.data
    
    // 调用后端API获取文件夹列表
    const folderResponse = await folderApi.getFolderList(currentFolderId.value)
    folderList.value = folderResponse.data
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  }
}

// 进入文件夹
const enterFolder = (folder) => {
  currentFolderId.value = folder.id
  breadcrumb.value.push({ id: folder.id, name: folder.name })
  loadFileList()
}

// 返回根目录
const goToRoot = () => {
  currentFolderId.value = 0
  breadcrumb.value = []
  loadFileList()
}

// 进入指定文件夹
const goToFolder = (folderId) => {
  const index = breadcrumb.value.findIndex(item => item.id === folderId)
  if (index !== -1) {
    breadcrumb.value = breadcrumb.value.slice(0, index + 1)
    currentFolderId.value = folderId
    loadFileList()
  }
}

// 显示上传对话框
const showUploadDialog = () => {
  selectedFiles.value = []
  uploadDialogVisible.value = true
}

// 处理文件选择
const handleFileChange = (file) => {
  if (file.status === 'ready') {
    selectedFiles.value.push(file)
  }
}

// 计算文件MD5
const calculateMd5 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    const spark = new SparkMD5.ArrayBuffer()
    
    reader.onload = (e) => {
      spark.append(e.target.result)
      resolve(spark.end())
    }
    
    reader.onerror = () => {
      reject(new Error('计算MD5失败'))
    }
    
    reader.readAsArrayBuffer(file.raw)
  })
}

// 确认上传
const confirmUpload = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploadLoading.value = true
  
  try {
    for (const file of selectedFiles.value) {
      // 计算文件MD5
      const md5 = await calculateMd5(file)
      
      // 检查文件是否已存在（秒传）
      const checkResult = await fileApi.checkMd5(md5, file.name)
      
      if (checkResult.data.exists) {
        ElMessage.success(`${file.name} 已存在，秒传成功`)
        continue
      }
      
      // 上传文件
      await fileApi.uploadSingle(file.raw, currentFolderId.value)
      ElMessage.success(`${file.name} 上传成功`)
    }
    
    // 重新加载文件列表
    await loadFileList()
    uploadDialogVisible.value = false
  } catch (error) {
    ElMessage.error('上传失败：' + (error.message || '未知错误'))
  } finally {
    uploadLoading.value = false
  }
}

// 新建文件夹
const createFolder = () => {
  folderForm.name = ''
  folderDialogVisible.value = true
}

// 确认创建文件夹
const confirmCreateFolder = async () => {
  const valid = await folderFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  try {
    await folderApi.createFolder(folderForm.name, currentFolderId.value)
    ElMessage.success('文件夹创建成功')
    folderDialogVisible.value = false
    await loadFileList()
  } catch (error) {
    ElMessage.error('创建文件夹失败')
  }
}

// 下载文件
const downloadFile = async (row) => {
  try {
    const response = await fileApi.downloadFile(row.id)
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 预览文件
const previewFile = async (row) => {
  try {
    currentPreviewFile.value = row
    const response = await fileApi.previewFile(row.id)
    
    if (response.data && response.data.url) {
      // 将 MinIO 内部 URL 转换为通过 Nginx 代理的 URL
      // MinIO 内部 URL 格式: http://minio:9000/...
      // 转换为: http://localhost/minio/...
      previewUrl.value = response.data.url.replace('http://minio:9000/', 'http://localhost/minio/')
      
      // 对于文本文件，直接获取内容并显示
      if (isText.value) {
        try {
          const textResponse = await fetch(previewUrl.value)
          // 明确使用 UTF-8 编码解析文本
          const textContent = await textResponse.text()
          previewContent.value = textContent
        } catch (error) {
          console.error('获取文本内容失败:', error)
          previewContent.value = '获取文本内容失败，请尝试下载查看'
        }
      } else {
        // 重置预览内容
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

// 下载当前预览的文件
const downloadCurrentFile = () => {
  if (currentPreviewFile.value) {
    downloadFile(currentPreviewFile.value)
  }
}

// 重命名文件或文件夹
const renameFile = (row) => {
  currentFile.value = row
  renameForm.name = row.name
  renameDialogVisible.value = true
}

// 确认重命名
const confirmRename = async () => {
  const valid = await renameFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  try {
    if (currentFile.value.type === 'file') {
      await fileApi.renameFile(currentFile.value.id, renameForm.name)
    } else {
      await folderApi.renameFolder(currentFile.value.id, renameForm.name)
    }
    ElMessage.success('重命名成功')
    renameDialogVisible.value = false
    await loadFileList()
  } catch (error) {
    ElMessage.error('重命名失败')
  }
}

// 删除文件或文件夹
const deleteFile = (row) => {
  ElMessageBox.confirm(`确定要删除${row.type === 'file' ? '该文件' : '该文件夹'}吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      if (row.type === 'file') {
        await fileApi.deleteFile(row.id)
      } else {
        await folderApi.deleteFolder(row.id)
      }
      ElMessage.success('删除成功')
      await loadFileList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 初始化
onMounted(() => {
  loadFileList()
})
</script>

<style scoped>
.file-manage {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.upload-demo {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}

.preview-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 20px;
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
  max-width: 500px;
}

.preview-text {
  width: 100%;
  max-height: 600px;
  overflow: auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.preview-unsupported {
  text-align: center;
  color: #909399;
}

.preview-unsupported p {
  margin: 20px 0;
}
</style>
