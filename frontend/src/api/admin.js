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
