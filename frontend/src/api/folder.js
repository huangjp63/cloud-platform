import request from './index'

export function createFolder(name, parentId = 0) {
  return request({
    url: '/folder/create',
    method: 'post',
    params: { name, parent_id: parentId }
  })
}

export function deleteFolder(folderId) {
  return request({
    url: `/folder/delete/${folderId}`,
    method: 'delete'
  })
}

export function renameFolder(folderId, name) {
  return request({
    url: `/folder/rename/${folderId}`,
    method: 'put',
    params: { name }
  })
}
