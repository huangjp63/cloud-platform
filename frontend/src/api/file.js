import request from './index'

export function checkMd5(md5, filename) {
  return request({
    url: '/file/check/md5',
    method: 'post',
    data: { md5, filename }
  })
}

export function uploadSingle(file, parentId = 0) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('parent_id', parentId)
  return request({
    url: '/file/upload/single',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getUploadedChunks(md5) {
  return request({
    url: '/file/upload/chunk',
    method: 'get',
    params: { md5 }
  })
}

export function uploadChunk(data) {
  return request({
    url: '/file/upload/chunk',
    method: 'post',
    data,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function mergeChunks(data) {
  return request({
    url: '/file/upload/merge',
    method: 'post',
    data
  })
}

export function downloadFile(fileId) {
  return request({
    url: `/file/download/${fileId}`,
    method: 'get',
    responseType: 'blob'
  })
}

export function deleteFile(fileId) {
  return request({
    url: `/file/delete/${fileId}`,
    method: 'delete'
  })
}

export function renameFile(fileId, name) {
  return request({
    url: `/file/rename/${fileId}`,
    method: 'put',
    params: { name }
  })
}

export function previewFile(fileId) {
  return request({
    url: `/file/preview/${fileId}`,
    method: 'get'
  })
}
