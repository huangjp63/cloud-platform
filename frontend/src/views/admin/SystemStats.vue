<template>
  <div class="system-stats">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTotalStatistics } from '@/api/admin'
import { ElMessage } from 'element-plus'

const stats = ref([
  { title: '总用户数', value: 0 },
  { title: '总文件数', value: 0 },
  { title: '总存储大小', value: '0 B' },
  { title: '今日活跃用户', value: 0 }
])

onMounted(async () => {
  try {
    const res = await getTotalStatistics()
    stats.value[0].value = res.data.total_users
    stats.value[1].value = res.data.total_files
    stats.value[2].value = res.data.total_size
    stats.value[3].value = res.data.today_active_users
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
})
</script>

<style scoped>
.system-stats {
  padding: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #409EFF;
}

.stat-title {
  margin-top: 10px;
  color: #909399;
}
</style>
