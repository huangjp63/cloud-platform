<template>
  <div class="analysis-view">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>文件统计</span>
          </template>
          <div class="chart-placeholder">图表区域 - 文件类型分布</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>用户行为统计</span>
          </template>
          <div class="chart-placeholder">图表区域 - 用户行为趋势</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="hot-files">
      <template #header>
        <span>热门文件排行</span>
      </template>
      <el-table :data="hotFiles" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="download_count" label="下载次数" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHotFiles } from '@/api/analysis'
import { ElMessage } from 'element-plus'

const hotFiles = ref([])

onMounted(async () => {
  try {
    const res = await getHotFiles()
    hotFiles.value = res.data
  } catch (error) {
    ElMessage.error('获取热门文件失败')
  }
})
</script>

<style scoped>
.analysis-view {
  padding: 20px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #909399;
}

.hot-files {
  margin-top: 20px;
}
</style>
