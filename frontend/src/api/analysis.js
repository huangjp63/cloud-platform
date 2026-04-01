import request from './index'

export function getFileStatistics(type = 'day') {
  return request({
    url: '/analysis/file',
    method: 'get',
    params: { type }
  })
}

export function getBehaviorStatistics(type = 'day') {
  return request({
    url: '/analysis/behavior',
    method: 'get',
    params: { type }
  })
}

export function getHotFiles() {
  return request({
    url: '/analysis/hot',
    method: 'get'
  })
}

export function getStatCard() {
  return request({
    url: '/analysis/card',
    method: 'get'
  })
}
