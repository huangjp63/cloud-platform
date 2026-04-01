import { defineStore } from 'pinia'

export const useFileStore = defineStore('file', {
  state: () => ({
    currentFolderId: 0,
    fileList: [],
    selectedFiles: []
  }),
  
  actions: {
    setCurrentFolder(folderId) {
      this.currentFolderId = folderId
    },
    
    setFileList(files) {
      this.fileList = files
    },
    
    setSelectedFiles(files) {
      this.selectedFiles = files
    },
    
    clearSelection() {
      this.selectedFiles = []
    }
  }
})
