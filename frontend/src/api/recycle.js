import request from './index'

export function getRecycleList() {
  return request({
    url: '/recycle/list',
    method: 'get'
  })
}

export function recoverItem(itemId) {
  return request({
    url: `/recycle/recover/${itemId}`,
    method: 'put'
  })
}

export function deletePermanently(itemId) {
  return request({
    url: `/recycle/delete/${itemId}`,
    method: 'delete'
  })
}

export function cleanExpired() {
  return request({
    url: '/recycle/clean',
    method: 'post'
  })
}

export function getFolderContents(folderId) {
  return request({
    url: `/recycle/folder/${folderId}`,
    method: 'get'
  })
}
