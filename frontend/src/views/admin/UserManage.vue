<template>
  <div class="user-manage">
    <el-card>
      <template #header>
        <span>用户列表</span>
      </template>
      <el-table :data="userList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllUsers } from '@/api/monitor'
import { ElMessage } from 'element-plus'

const userList = ref([])

onMounted(async () => {
  try {
    const res = await getAllUsers()
    userList.value = res.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
})
</script>

<style scoped>
.user-manage {
  padding: 20px;
}
</style>
