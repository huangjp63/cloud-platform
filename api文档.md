
# Cloud-Platform 轻量级云盘系统 API 文档
## 文档说明
本文档基于 Cloud-Platform 轻量级云盘系统（简易权限版）需求文档生成，定义系统所有后端接口规范，采用 RESTful 风格，前后端数据交互格式为 JSON，权限基于 JWT 令牌校验，区分普通用户(user)与管理员(admin)。

## 基础信息
- 基础URL：`http://服务器IP:8000/api/v1`
- 请求头：`Authorization: Bearer {JWT令牌}`（登录接口除外）
- 字符编码：UTF-8
- Content-Type：`application/json`（文件上传为 `multipart/form-data`）
- 权限角色：`user`（普通用户）、`admin`（管理员）

---

## 通用响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```
- `code`：状态码，200 成功，4xx 客户端错误，5xx 服务端错误
- `message`：提示信息
- `data`：业务数据

---

## 通用错误码
| 错误码 | 说明 |
|--------|------|
| 401    | 未登录/令牌无效/令牌过期 |
| 403    | 权限不足，无法访问该接口 |
| 404    | 接口/资源不存在 |
| 400    | 请求参数错误 |
| 500    | 服务器内部错误 |

---

# 一、用户模块
## 1.1 用户注册
- 请求方式：POST
- 请求路径：`/user/register`
- 权限：无需登录

**请求体**
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": null
}
```

---

## 1.2 用户登录
- 请求方式：POST
- 请求路径：`/user/login`
- 权限：无需登录

**请求体**
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "role": "user",
    "username": "testuser"
  }
}
```

---

## 1.3 退出登录
- 请求方式：POST
- 请求路径：`/user/logout`
- 权限：user/admin

**响应**
```json
{
  "code": 200,
  "message": "退出成功",
  "data": null
}
```

---

## 1.4 获取个人信息
- 请求方式：GET
- 请求路径：`/user/info`
- 权限：user/admin

**响应**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "role": "user",
    "create_time": "2026-04-01 12:00:00",
    "last_login_time": "2026-04-01 12:01:00"
  }
}
```

---

# 二、文件夹管理模块
## 2.1 创建文件夹
- 请求方式：POST
- 请求路径：`/folder/create`
- 权限：user/admin

**请求体**
```json
{
  "name": "我的文档",
  "parent_id": 0
}
```
**响应**：返回文件夹 ID 及基础信息

---

## 2.2 删除文件夹
- 请求方式：DELETE
- 请求路径：`/folder/delete/{folder_id}`
- 权限：user/admin（仅管理员可删除所有用户文件夹）
**响应**：删除成功，移入回收站

---

## 2.3 重命名文件夹
- 请求方式：PUT
- 请求路径：`/folder/rename/{folder_id}`
- 权限：user/admin

**请求体**
```json
{
  "name": "新文件夹名称"
}
```

---

# 三、文件管理模块
## 3.1 秒传校验
- 请求方式：POST
- 请求路径：`/file/check/md5`
- 权限：user/admin

**请求体**
```json
{
  "md5": "e10adc3949ba59abbe56e057f20f883e",
  "filename": "test.mp4"
}
```
**响应**：`exist:true` 表示可秒传，`false` 需正常上传

---

## 3.2 单文件上传
- 请求方式：POST
- 请求路径：`/file/upload/single`
- 权限：user/admin
- Content-Type：`multipart/form-data`
- 请求参数：`file`(文件)、`parent_id`(父文件夹ID)
**响应**：返回文件存储信息

---

## 3.3 断点续传（分片上传）
### 3.3.1 获取已上传分片
- 请求方式：GET
- 请求路径：`/file/upload/chunk?md5={文件MD5}`
- 权限：user/admin
**响应**：返回已上传分片索引列表

### 3.3.2 上传分片
- 请求方式：POST
- 请求路径：`/file/upload/chunk`
- 权限：user/admin
- 请求参数：`md5`、`index`(分片序号)、`total`(总分片数)、`chunk`(分片文件)

### 3.3.3 合并分片
- 请求方式：POST
- 请求路径：`/file/upload/merge`
- 权限：user/admin

**请求体**
```json
{
  "md5": "文件MD5",
  "filename": "文件名",
  "parent_id": 0,
  "total": 总分片数
}
```

---

## 3.4 文件下载
- 请求方式：GET
- 请求路径：`/file/download/{file_id}`
- 权限：user/admin（仅管理员可下载所有用户文件）
**响应**：文件流

---

## 3.5 文件批量打包下载
- 请求方式：POST
- 请求路径：`/file/download/batch`
- 权限：user/admin

**请求体**
```json
{
  "file_ids": [1,2,3]
}
```

---

## 3.6 文件删除（移入回收站）
- 请求方式：DELETE
- 请求路径：`/file/delete/{file_id}`
- 权限：user/admin

---

## 3.7 文件重命名
- 请求方式：PUT
- 请求路径：`/file/rename/{file_id}`
- 权限：user/admin

**请求体**
```json
{
  "name": "新文件名"
}
```

---

## 3.8 文件在线预览
- 请求方式：GET
- 请求路径：`/file/preview/{file_id}`
- 权限：user/admin
- 支持类型：图片(JPG/PNG/GIF)、文本(TXT/MD)、视频(MP4/AVI)

---

# 四、回收站模块
## 4.1 查询回收站列表
- 请求方式：GET
- 请求路径：`/recycle/list`
- 权限：user/admin（管理员查看所有用户数据）
**响应**：返回回收站文件/文件夹列表

---

## 4.2 恢复文件/文件夹
- 请求方式：PUT
- 请求路径：`/recycle/recover/{id}`
- 权限：user/admin

---

## 4.3 彻底删除
- 请求方式：DELETE
- 请求路径：`/recycle/delete/{id}`
- 权限：user/admin

---

## 4.4 手动清理过期文件（管理员）
- 请求方式：POST
- 请求路径：`/recycle/clean`
- 权限：admin

---

# 五、大数据分析模块
## 5.1 获取文件统计数据
- 请求方式：GET
- 请求路径：`/analysis/file?type=day/week/month`
- 权限：user/admin（user 看个人，admin 看汇总）
**响应**：上传数、总大小、类型分布

---

## 5.2 获取用户行为统计
- 请求方式：GET
- 请求路径：`/analysis/behavior?type=day/week/month`
- 权限：user/admin

---

## 5.3 获取热门文件排行
- 请求方式：GET
- 请求路径：`/analysis/hot`
- 权限：user/admin

---

## 5.4 获取核心统计卡片
- 请求方式：GET
- 请求路径：`/analysis/card`
- 权限：user/admin

---

# 六、系统监控模块
## 6.1 获取服务器资源监控
- 请求方式：GET
- 请求路径：`/monitor/resource`
- 权限：user/admin（user 看基础，admin 看完整）
**响应**：CPU/内存/磁盘使用率

---

## 6.2 获取服务运行状态
- 请求方式：GET
- 请求路径：`/monitor/service`
- 权限：user/admin（user 看核心服务，admin 看所有服务）
**响应**：MySQL/Redis/MinIO/ES/Spark 等服务状态

---

# 七、管理员专属模块
## 7.1 获取所有用户列表
- 请求方式：GET
- 请求路径：`/admin/user/list`
- 权限：admin

---

## 7.2 获取系统整体统计
- 请求方式：GET
- 请求路径：`/admin/analysis/total`
- 权限：admin

---

