import request from './index'

export function getResourceMonitor() {
  return request({
    url: '/monitor/resource',
    method: 'get'
  })
}

export function getServiceStatus() {
  return request({
    url: '/monitor/service',
    method: 'get'
  })
}
