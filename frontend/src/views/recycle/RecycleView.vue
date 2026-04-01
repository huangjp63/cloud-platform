<template>
  <div class="recycle-view">
    <el-card>
      <template #header>
        <div class="header">
          <span>回收站</span>
          <el-button type="danger" @click="cleanExpired" v-if="userStore.isAdmin">
            清理过期文件
          </el-button>
        </div>
      </template>
      
      <el-table :data="recycleList" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="item_type" label="类型" width="100" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="delete_time" label="删除时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="recoverItem(row)">恢复</el-button>
            <el-button link type="danger" @click="deletePermanently(row)">彻底删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecycleList, recoverItem as recoverApi, deletePermanently as deleteApi, cleanExpired as cleanApi } from '@/api/recycle'
import { formatFileSize } from '@/utils/format'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const recycleList = ref([])

const fetchRecycleList = async () => {
  try {
    const res = await getRecycleList()
    recycleList.value = res.data
  } catch (error) {
    ElMessage.error('获取回收站列表失败')
  }
}

const recoverItem = async (row) => {
  try {
    await recoverApi(row.id)
    ElMessage.success('恢复成功')
    fetchRecycleList()
  } catch (error) {
    ElMessage.error('恢复失败')
  }
}

const deletePermanently = async (row) => {
  try {
    await ElMessageBox.confirm('彻底删除后无法恢复，确定要删除吗？', '警告', {
      type: 'warning'
    })
    await deleteApi(row.id)
    ElMessage.success('已彻底删除')
    fetchRecycleList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const cleanExpired = async () => {
  try {
    const res = await cleanApi()
    ElMessage.success(res.message)
    fetchRecycleList()
  } catch (error) {
    ElMessage.error('清理失败')
  }
}

onMounted(() => {
  fetchRecycleList()
})
</script>

<style scoped>
.recycle-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
