<template>
  <div class="monitor-view">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>CPU 使用率</span>
          </template>
          <div class="monitor-value">{{ resource.cpu_usage }}%</div>
          <el-progress :percentage="resource.cpu_usage" :color="getProgressColor(resource.cpu_usage)" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>内存使用率</span>
          </template>
          <div class="monitor-value">{{ resource.memory_usage }}%</div>
          <el-progress :percentage="resource.memory_usage" :color="getProgressColor(resource.memory_usage)" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>磁盘使用率</span>
          </template>
          <div class="monitor-value">{{ resource.disk_usage }}%</div>
          <el-progress :percentage="resource.disk_usage" :color="getProgressColor(resource.disk_usage)" />
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="service-status">
      <template #header>
        <span>服务状态</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="(status, service) in services" :key="service">
          <div class="service-item">
            <span class="service-name">{{ service }}</span>
            <el-tag :type="status === 'running' ? 'success' : 'danger'">
              {{ status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getResourceMonitor, getServiceStatus } from '@/api/monitor'
import { ElMessage } from 'element-plus'

const resource = reactive({
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0
})

const services = ref({})

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const fetchMonitorData = async () => {
  try {
    const res1 = await getResourceMonitor()
    Object.assign(resource, res1.data)
    
    const res2 = await getServiceStatus()
    services.value = res2.data
  } catch (error) {
    ElMessage.error('获取监控数据失败')
  }
}

onMounted(() => {
  fetchMonitorData()
})
</script>

<style scoped>
.monitor-view {
  padding: 20px;
}

.monitor-value {
  font-size: 36px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 20px;
  color: #303133;
}

.service-status {
  margin-top: 20px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.service-name {
  font-weight: 500;
  text-transform: capitalize;
}
</style>
