<template>
  <div class="home-view">
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: card.color }">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="welcome-card">
      <h2>欢迎使用 Cloud-Platform 云盘系统</h2>
      <p>一个轻量级、高效的私人云盘解决方案</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStatCard } from '@/api/analysis'
import { Files, Upload, Download, User } from '@element-plus/icons-vue'
import { formatFileSize } from '@/utils/format'

const statCards = ref([
  { title: '文件总数', value: '0', icon: 'Files', color: '#409EFF' },
  { title: '总大小', value: '0 B', icon: 'Upload', color: '#67C23A' },
  { title: '今日上传', value: '0', icon: 'Download', color: '#E6A23C' },
  { title: '今日登录', value: '0', icon: 'User', color: '#F56C6C' }
])

onMounted(async () => {
  try {
    const res = await getStatCard()
    statCards.value[0].value = res.data.total_files
    statCards.value[1].value = formatFileSize(res.data.total_size)
    statCards.value[2].value = res.data.today_uploads
    statCards.value[3].value = res.data.today_logins
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
})
</script>

<style scoped>
.home-view {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  margin-left: 16px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-title {
  font-size: 14px;
  color: #909399;
}

.welcome-card {
  text-align: center;
  padding: 40px;
}

.welcome-card h2 {
  margin-bottom: 16px;
  color: #303133;
}

.welcome-card p {
  color: #606266;
}
</style>
