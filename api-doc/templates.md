# 提示词方案接口文档

## 创建提示词方案

**接口**：`POST /api/templates/`

**功能**：使用方案名称、方案内容新建方案，方案名称不可重复

**请求体**：

```json
{
    "name": "string",    // 方案名称，必填
    "content": "string"  // 方案内容，必填
}
```

**响应**：

```json
{
    "id": 0,
    "name": "string",
    "content": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

**错误响应**：

- 400：方案名称已存在

## 编辑提示词方案

**接口**： `PUT /api/templates/{template_id}`

**功能**：`编辑方案名称、方案内容，方案名称不可重复`

**参数**：

- template_id ：方案ID（路径参数）

**请求体**：

```json
{
    "name": "string",    // 方案名称，可选
    "content": "string"  // 方案内容，可选
}
```

**响应**：

```json
{
    "id": 0,
    "name": "string",
    "content": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

**错误响应**：

- 404：方案不存在
- 400：方案名称已存在

## 删除提示词方案

**接口**： `DELETE /api/templates/{template_id}`

**功能**：删除指定的提示词方案

**参数**：

- template_id ：方案ID（路径参数）

**响应**：

```json
{
    "message": "Template deleted successfully"
}
```

错误响应 ：

- 404：方案不存在

## 查询提示词方案列表

**接口**： GET `/api/templates/`

**功能**：根据更新时间倒序展示所有方案，包含方案内容，分页展示，每页展示20条数据，可以用方案名称筛选

**查询参数**：

- name ：方案名称，模糊匹配（可选）
- page ：页码，默认为1

**响应**：

```json
[
    {
        "id": 0,
        "name": "string",
        "content": "string",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

**说明**：

- 列表按更新时间倒序排序
- 每页默认显示20条数据
- 支持通过方案名称进行模糊搜索