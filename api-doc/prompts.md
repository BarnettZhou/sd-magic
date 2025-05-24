# 提示词接口文档

## 提示词管理

### 创建提示词

**接口**：`POST /api/prompts/`

**请求体**：

```json
{
    "original_text": "string",      // 提示词原文，必填
    "chinese_translation": "string", // 中文翻译，可选
    "category_id": 0               // 分类ID，必填
}
```

**响应**：

```json
{
    "id": 0,
    "original_text": "string",
    "chinese_translation": "string",
    "category_id": 0
}
```

**错误响应**：

- 400：提示词原文已存在
- 404：分类不存在

### 更新提示词

**接口**： `PUT /api/prompts/{prompt_id}`

**参数**：

- prompt_id ：提示词ID（路径参数）

**请求体**：

```json
{
    "original_text": "string",      // 提示词原文，可选
    "chinese_translation": "string", // 中文翻译，可选
    "category_id": 0               // 分类ID，可选
}
```

**响应**：

```json
{
    "id": 0,
    "original_text": "string",
    "chinese_translation": "string",
    "category_id": 0
}
```

**错误响应**：

- 404：提示词不存在
- 400：提示词原文已存在

### 删除提示词

**接口**： DELETE /api/prompts/{prompt_id}

**参数**：

- prompt_id ：提示词ID（路径参数）

**响应**：

```
{
    "message": "Prompt deleted successfully"
}
```

**错误响应**：

- 404：提示词不存在

### 查询提示词列表

**接口**： GET `/api/prompts/`

**查询参数**：

- category_id ：分类ID（可选）
- search ：搜索关键词，会匹配原文和翻译（可选）
- page ：页码，默认为1
- per_page ：每页数量，默认为20

**响应**：

```json
[
    {
        "id": 0,
        "original_text": "string",
        "chinese_translation": "string",
        "category_id": 0
    }
]
```
