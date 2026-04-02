<template>
  <div class="file-manage">
    <el-card>
      <template #header>
        <div class="header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/file' }">全部文件</el-breadcrumb-item>
          </el-breadcrumb>
          <div class="actions">
            <el-button type="primary" @click="showUploadDialog">上传文件</el-button>
            <el-button @click="createFolder">新建文件夹</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="fileList" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="downloadFile(row)">下载</el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { formatFileSize } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import * as fileApi from '@/api/file'
import * as folderApi from '@/api/folder'
import SparkMD5 from 'spark-md5'

const fileList = ref([])
const uploadDialogVisible = ref(false)
const folderDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const uploadLoading = ref(false)
const selectedFiles = ref([])
const currentFile = ref(null)

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
    const response = await fileApi.getFileList(0)
    fileList.value = response.data
  } catch (error) {
    ElMessage.error('获取文件列表失败')
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
      await fileApi.uploadSingle(file.raw, 0)
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
    await folderApi.createFolder(folderForm.name, 0)
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

// 重命名文件
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
    await fileApi.renameFile(currentFile.value.id, renameForm.name)
    ElMessage.success('重命名成功')
    renameDialogVisible.value = false
    await loadFileList()
  } catch (error) {
    ElMessage.error('重命名失败')
  }
}

// 删除文件
const deleteFile = (row) => {
  ElMessageBox.confirm('确定要删除该文件吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await fileApi.deleteFile(row.id)
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
</style>
