# 分类管理 API

## 创建分类

### 请求

```http
POST /api/categories/
```

### 请求参数

|参数名|类型|必填|描述|
|---|---|---|---|
|name|string|是|分类名称|
|parent_id|integer|否|父级分类ID|

### 响应

``` json
{
    "id": 1,
    "name": "示例分类",
    "parent_id": null,
    "is_default": false,
    "children": []
}
```

### 错误响应

- 400: 分类名称已存在
- 400: 不能在默认分类下创建子分类
- 404: 父级分类不存在

## 编辑分类

### 请求

```
PUT /api/categories/{category_id}
```

### 请求参数

|参数名|类型|必填|描述|
|---|---|---|---|
|name|string|是|分类名称|
|parent_id|integer|否|父级分类ID|

### 响应

```json
{
    "id": 1,
    "name": "新分类名称",
    "parent_id": null,
    "is_default": false,
    "children": []
}
```

### 错误响应

- 400: 分类名称已存在
- 400: 不能修改默认分类
- 404: 分类不存在

## 删除分类

### 请求

```http
DELETE /api/categories/{category_id}
```

### 响应

```
{
    "message": "分类删除成功"
}
```

### 错误响应

- 400: 不能删除默认分类
- 404: 分类不存在

## 查询所有分类

### 请求

```http
GET /api/categories/
```

### 响应

```json
[
    {
        "id": 1,
        "name": "默认分类",
        "parent_id": null,
        "is_default": true,
        "children": []
    },
    {
        "id": 2,
        "name": "父级分类",
        "parent_id": null,
        "is_default": false,
        "children": [
            {
                "id": 3,
                "name": "子级分类",
                "parent_id": 2,
                "is_default": false,
                "children": []
            }
        ]
    }
]
```
