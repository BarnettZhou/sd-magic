<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { TemplateData } from '@/types/template'
import { API_HOST } from '@/config/api'

// 模板数据
const templates = ref<TemplateData[]>([])

// 编辑表单相关
const templateFormVisible = ref(false)
const templateForm = ref({
  id: null as number | null,
  name: '',
  content: ''
})
const isEditing = ref(false)

// 获取所有模板
const fetchTemplates = async () => {
  try {
    const response = await fetch(`${API_HOST}/api/templates/`)
    if (!response.ok) throw new Error('获取模板列表失败')
    templates.value = await response.json()
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  }
}

// 创建模板
const createTemplate = async () => {
  if (!templateForm.value.name.trim() || !templateForm.value.content.trim()) {
    ElMessage.warning('请填写完整的模板信息')
    return
  }

  try {
    const response = await fetch(`${API_HOST}/api/templates/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '创建模板失败')
    }

    ElMessage.success('创建模板成功')
    templateFormVisible.value = false
    await fetchTemplates()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建模板失败')
  }
}

// 更新模板
const updateTemplate = async () => {
  if (!templateForm.value.id) return

  try {
    const response = await fetch(`${API_HOST}/api/templates/${templateForm.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '更新模板失败')
    }

    ElMessage.success('更新模板成功')
    templateFormVisible.value = false
    await fetchTemplates()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '更新模板失败')
  }
}

// 删除模板
const deleteTemplate = async (id: number) => {
  try {
    const confirmed = await ElMessageBox.confirm('确定删除该方案吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (!confirmed) return

    const response = await fetch(`${API_HOST}/api/templates/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '删除模板失败')
    }

    ElMessage.success('删除模板成功')
    await fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '删除模板失败')
    }
  }
}

// 打开编辑表单
const openEditForm = (template: TemplateData) => {
  isEditing.value = true
  templateForm.value = {
    id: template.id,
    name: template.name,
    content: template.content
  }
  templateFormVisible.value = true
}

// 提交表单
const handleTemplateSubmit = async () => {
  if (isEditing.value) {
    await updateTemplate()
  } else {
    await createTemplate()
  }
}

// 初始化
onMounted(() => {
  fetchTemplates()
})
</script>

<template>
  <el-container class="el-container">
    <!-- 模板列表 -->
    <el-table :data="templates" style="width: 100%">
      <el-table-column prop="name" label="方案名称" width="200" />
      <el-table-column prop="content" label="方案内容" min-width="400">
        <template #default="scope">
          {{ scope.row.content.length > 80 ? scope.row.content.slice(0, 80) + '...' : scope.row.content }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button :icon="Edit" circle @click="openEditForm(scope.row)" />
          <el-button :icon="Delete" circle type="danger" @click="deleteTemplate(scope.row.id)" />
        </template>
      </el-table-column>
    </el-table>

    <!-- 模板表单弹窗 -->
    <el-dialog v-model="templateFormVisible" :title="isEditing ? '编辑方案' : '新建方案'" width="600px">
      <el-form :model="templateForm" label-width="80px">
        <el-form-item label="方案名称" required>
          <el-input v-model="templateForm.name" placeholder="请输入方案名称" />
        </el-form-item>
        <el-form-item label="方案内容" required>
          <el-input v-model="templateForm.content" type="textarea" :rows="5" placeholder="请输入方案内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateFormVisible = false">取消</el-button>
          <el-button type="primary" @click="handleTemplateSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<style scoped>
.template-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.template-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.template-name {
  margin-bottom: 10px;
  font-size: 16px;
  color: #303133;
}

.template-content-text {
  flex: 1;
  overflow: hidden;
  display: flex;
  align-items: center;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-family: monospace;
  line-height: 1.5;
  text-overflow: ellipsis;
}

.template-actions {
  margin-top: auto;
  padding: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>