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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatFileSize } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const fileList = ref([])

const showUploadDialog = () => {
  ElMessage.info('上传功能开发中')
}

const createFolder = () => {
  ElMessage.info('创建文件夹功能开发中')
}

const downloadFile = (row) => {
  ElMessage.info('下载功能开发中')
}

const renameFile = (row) => {
  ElMessage.info('重命名功能开发中')
}

const deleteFile = (row) => {
  ElMessageBox.confirm('确定要删除该文件吗？', '提示', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {})
}
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
</style>
