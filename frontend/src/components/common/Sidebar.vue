<template>
  <div class="sidebar">
    <el-menu
      :default-active="activeMenu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/home">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/file">
        <el-icon><Folder /></el-icon>
        <span>文件管理</span>
      </el-menu-item>
      <el-menu-item index="/recycle">
        <el-icon><Delete /></el-icon>
        <span>回收站</span>
      </el-menu-item>
      <el-menu-item index="/analysis">
        <el-icon><DataAnalysis /></el-icon>
        <span>数据分析</span>
      </el-menu-item>
      <el-menu-item index="/monitor">
        <el-icon><Monitor /></el-icon>
        <span>系统监控</span>
      </el-menu-item>
      <el-menu-item v-if="userStore.isAdmin" index="/admin/users">
        <el-icon><Setting /></el-icon>
        <span>管理后台</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { HomeFilled, Folder, Delete, DataAnalysis, Monitor, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.el-menu {
  border-right: none;
}
</style>
