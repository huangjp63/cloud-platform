import request from './index'

export function getAllUsers() {
  return request({
    url: '/admin/user/list',
    method: 'get'
  })
}

export function getTotalStatistics() {
  return request({
    url: '/admin/analysis/total',
    method: 'get'
  })
}

export function getAllFiles() {
  return request({
    url: '/admin/file/list',
    method: 'get'
  })
}

export function deleteUser(userId) {
  return request({
    url: `/admin/user/${userId}`,
    method: 'delete'
  })
}

export function updateUserRole(userId, role) {
  return request({
    url: `/admin/user/${userId}/role`,
    method: 'put',
    params: { role }
  })
}

export function deleteFile(fileId) {
  return request({
    url: `/admin/file/${fileId}`,
    method: 'delete'
  })
}

