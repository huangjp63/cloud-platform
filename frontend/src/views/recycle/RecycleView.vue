<template>
  <div class="recycle-view">
    <el-card>
      <template #header>
        <div class="header">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item @click="goToRoot">回收站</el-breadcrumb-item>
              <el-breadcrumb-item 
                v-for="(item, index) in breadcrumb" 
                :key="item.id"
                @click="goToFolder(item.id, index)"
              >
                {{ item.name }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <el-button type="danger" @click="cleanExpired" v-if="userStore.isAdmin">
            清理过期文件
          </el-button>
        </div>
      </template>
      
      <el-table :data="currentList" style="width: 100%">
        <el-table-column prop="name" label="文件名">
          <template #default="{ row }">
	    <span v-if="row.type === 'folder' || row.item_type === 'folder'" style="display: flex; align-items: center; gap: 8px; cursor: pointer" @click="enterFolder(row)">
              <el-icon><Folder /></el-icon>
              <span>{{ row.name }}</span>
            </span>
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="item_type" label="类型" width="100">
          <template #default="{ row }">
            {{ row.item_type || row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="delete_time" label="删除时间" width="180">
          <template #default="{ row }">
            {{ row.delete_time || '-' }}
          </template>
        </el-table-column>
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
import { ref, onMounted, computed } from 'vue'
import { getRecycleList, recoverItem as recoverApi, deletePermanently as deleteApi, cleanExpired as cleanApi, getFolderContents } from '@/api/recycle'
import { formatFileSize } from '@/utils/format'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder } from '@element-plus/icons-vue'

const userStore = useUserStore()
const recycleList = ref([])
const breadcrumb = ref([])
const currentFolderId = ref(0)

const currentList = computed(() => {
  if (currentFolderId.value === 0) {
    return recycleList.value
  }
  return folderContents.value
})

const folderContents = ref([])

const fetchRecycleList = async () => {
  try {
    const res = await getRecycleList()
    recycleList.value = res.data
  } catch (error) {
    ElMessage.error('获取回收站列表失败')
  }
}

const enterFolder = async (row) => {
  try {
    const folderId = row.item_id || row.id
    const res = await getFolderContents(folderId)
    if (res.data) {
      currentFolderId.value = folderId
      folderContents.value = res.data.contents
      breadcrumb.value.push({
        id: folderId,
        name: row.name
      })
    }
  } catch (error) {
    ElMessage.error('获取文件夹内容失败')
  }
}

const goToRoot = () => {
  currentFolderId.value = 0
  breadcrumb.value = []
  folderContents.value = []
}

const goToFolder = (folderId, index) => {
  if (index === breadcrumb.value.length - 1) {
    return
  }
  
  breadcrumb.value = breadcrumb.value.slice(0, index + 1)
  enterFolder({ id: folderId, name: breadcrumb.value[index].name })
}

const recoverItem = async (row) => {
  try {
    await recoverApi(row.id)
    ElMessage.success('恢复成功')
    if (currentFolderId.value === 0) {
      fetchRecycleList()
    } else {
      enterFolder({ id: currentFolderId.value, name: breadcrumb.value[breadcrumb.value.length - 1].name })
    }
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
    if (currentFolderId.value === 0) {
      fetchRecycleList()
    } else {
      enterFolder({ id: currentFolderId.value, name: breadcrumb.value[breadcrumb.value.length - 1].name })
    }
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

.breadcrumb {
  cursor: pointer;
}

.breadcrumb .el-breadcrumb-item {
  cursor: pointer;
}
</style>
