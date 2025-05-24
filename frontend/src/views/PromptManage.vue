<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Plus, Edit, Delete, ShoppingCart, Search, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { CategoryData } from '@/types/category'
import type { PromptData } from '@/types/prompt'
import { API_HOST } from '@/config/api'

// 分类数据
const categories = ref<CategoryData[]>([])

// 选中的分类
const selectedCategory = ref<CategoryData | null>(null)

// 分类表单
const categoryFormVisible = ref(false)
const categoryForm = ref({
  name: '',
  parent_id: null as number | null
})
const isEditing = ref(false)
const editingCategoryId = ref<number | null>(null)

// 获取所有分类
const fetchCategories = async () => {
  try {
    const response = await fetch(`${API_HOST}/api/categories/`)
    if (!response.ok) throw new Error('获取分类失败')
    categories.value = await response.json()
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

// 创建分类
const createCategory = async () => {
  try {
    const response = await fetch(`${API_HOST}/api/categories/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(categoryForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '创建分类失败')
    }

    ElMessage.success('创建分类成功')
    categoryFormVisible.value = false
    await fetchCategories()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建分类失败')
  }
}

// 更新分类
const updateCategory = async () => {
  if (!editingCategoryId.value) return

  try {
    const response = await fetch(`${API_HOST}/api/categories/${editingCategoryId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(categoryForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '更新分类失败')
    }

    ElMessage.success('更新分类成功')
    categoryFormVisible.value = false
    await fetchCategories()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '更新分类失败')
  }
}

// 删除分类
const deleteCategory = async (id: number) => {
  try {
    const confirmed = await ElMessageBox.confirm('确认删除分类？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (!confirmed) return

    const response = await fetch(`${API_HOST}/api/categories/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '删除分类失败')
    }

    ElMessage.success('删除分类成功')
    await fetchCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '删除分类失败')
    }
  }
}

// 打开新建分类表单
const openCreateForm = () => {
  isEditing.value = false
  editingCategoryId.value = null
  categoryForm.value = {
    name: '',
    parent_id: null
  }
  categoryFormVisible.value = true
}

// 打开编辑分类表单
const openEditForm = (category: CategoryData) => {
  isEditing.value = true
  editingCategoryId.value = category.id
  categoryForm.value = {
    name: category.name,
    parent_id: category.parentId
  }
  categoryFormVisible.value = true
}

// 提交表单
const handleCategorySubmit = async () => {
  if (isEditing.value) {
    await updateCategory()
  } else {
    await createCategory()
  }
}

// 分类选择处理
const handleCategorySelect = (category: CategoryData | null) => {
  selectedCategory.value = category
}

// 搜索相关
const searchQuery = ref('')

// 分页相关
const currentPage = ref(1)
const perPage = ref(20)
const loading = ref(false)
const noMoreData = ref(false)
const total = ref(0)

// 提示词表单
const promptFormVisible = ref(false)
const promptForm = ref({
  original_text: '',
  chinese_translation: '',
  category_id: null as number | null
})
const isEditingPrompt = ref(false)
const editingPromptId = ref<number | null>(null)

const prompts = ref<Array<{
  id: number
  original_text: string
  chinese_translation: string
  category_id: number
  categoryPath?: string[]
}>>([])

// 获取提示词列表
const fetchPrompts = async (page = 1) => {
  try {
    loading.value = true
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.value.toString(),
      ...(selectedCategory.value?.id && { category_id: selectedCategory.value.id.toString() }),
      ...(searchQuery.value && { search: searchQuery.value })
    })

    const response = await fetch(`${API_HOST}/api/prompts/?${params.toString()}`)
    if (!response.ok) throw new Error('获取提示词失败')
    const data = await response.json()
    
    // 处理两种响应格式：
    // 1. 直接返回数组：[{}]
    // 2. 返回分页对象：{ results: [], count: 0, next: null }
    const results = Array.isArray(data) ? data : data.results || []
    
    // 如果是第一页，替换数据；否则追加数据
    if (page === 1) {
      prompts.value = results
    } else {
      prompts.value = [...prompts.value, ...results]
    }
    
    total.value = Array.isArray(data) ? results.length : data.count || 0
    noMoreData.value = Array.isArray(data) ? false : data.next === null
  } catch (error) {
    ElMessage.error('获取提示词列表失败')
  } finally {
    loading.value = false
  }
}

// 创建提示词
const createPrompt = async () => {
  try {
    const response = await fetch(`${API_HOST}/api/prompts/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(promptForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '创建提示词失败')
    }

    ElMessage.success('创建提示词成功')
    promptFormVisible.value = false
    currentPage.value = 1 // 重置到第一页
    await fetchPrompts(1)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建提示词失败')
  }
}

// 更新提示词
const updatePrompt = async () => {
  if (!editingPromptId.value) return

  try {
    const response = await fetch(`${API_HOST}/api/prompts/${editingPromptId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(promptForm.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '更新提示词失败')
    }

    ElMessage.success('更新提示词成功')
    promptFormVisible.value = false
    // 更新后总是从第1页开始重新获取数据，以防止数据重复
    currentPage.value = 1
    noMoreData.value = false
    await fetchPrompts(1)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '更新提示词失败')
  }
}

// 删除提示词
const deletePrompt = async (id: number) => {
  try {
    const confirmed = await ElMessageBox.confirm('是否删除提示词？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (!confirmed) return

    const response = await fetch(`${API_HOST}/api/prompts/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '删除提示词失败')
    }

    ElMessage.success('删除提示词成功')
    await fetchPrompts(currentPage.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '删除提示词失败')
    }
  }
}

// 打开新建提示词表单
const openCreatePromptForm = () => {
  isEditingPrompt.value = false
  editingPromptId.value = null
  promptForm.value = {
    original_text: '',
    chinese_translation: '',
    category_id: selectedCategory.value?.id || null
  }
  promptFormVisible.value = true
}

// 打开编辑提示词表单
const openEditPromptForm = (prompt: typeof prompts.value[0]) => {
  isEditingPrompt.value = true
  editingPromptId.value = prompt.id
  promptForm.value = {
    original_text: prompt.original_text,
    chinese_translation: prompt.chinese_translation,
    category_id: prompt.category_id
  }
  promptFormVisible.value = true
}

// 提交表单
const handlePromptSubmit = async () => {
  if (isEditingPrompt.value) {
    await updatePrompt()
  } else {
    await createPrompt()
  }
}

// 监听分类选择变化
watch(selectedCategory, () => {
  currentPage.value = 1
  noMoreData.value = false
  fetchPrompts(1)
})

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  noMoreData.value = false
  fetchPrompts()
}

const updatePrompts = () => {
  currentPage.value = 1
  noMoreData.value = false
  fetchPrompts()
}

// 滚动加载
const handleScroll = (event: Event) => {
  const element = event.target as HTMLElement
  if (loading.value || noMoreData.value) return

  const { scrollHeight, scrollTop, clientHeight } = element
  if (scrollHeight - scrollTop - clientHeight < 50) {
    fetchPrompts(currentPage.value + 1)
  }
}

// 初始化
onMounted(() => {
  fetchCategories(),
  fetchPrompts()
})

// 购物车数据
const cartVisible = ref(false)
interface CartItem {
  original_text: string
  chinese_translation: string
}

const cartItems = ref<CartItem[]>([])

// 添加到购物车
const addToCart = (prompt: typeof prompts.value[0]) => {
  const existingItem = cartItems.value.find(item => item.original_text === prompt.original_text)
  if (existingItem) {
    ElMessage.warning('提示词已添加到购物车')
    return
  }
  
  cartItems.value.push({
    original_text: prompt.original_text,
    chinese_translation: prompt.chinese_translation
  })
  ElMessage.success('已添加到购物车')
}

// 从购物车移除
const removeFromCart = (text: string) => {
  const index = cartItems.value.findIndex(item => item.original_text === text)
  if (index > -1) {
    cartItems.value.splice(index, 1)
    ElMessage.success('已从购物车移除')
  }
}

// 清空购物车
const clearCart = () => {
  cartItems.value = []
  ElMessage.success('已清空购物车')
}

// 保存方案表单
const templateFormVisible = ref(false)
const templateForm = ref({
  name: ''
})

// 保存为方案
const saveAsPlan = () => {
  if (!cartItems.value || cartItems.value.length === 0) {
    ElMessage.warning('购物车为空')
    return
  }
  
  templateFormVisible.value = true
  templateForm.value.name = ''
}

// 保存方案
const saveTemplate = async () => {
  if (!templateForm.value.name.trim()) {
    ElMessage.warning('请输入方案名称')
    return
  }

  try {
    const formattedContent = cartItems.value.map(item => item.original_text).join(', ') + ','
    
    const response = await fetch(`${API_HOST}/api/templates/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: templateForm.value.name,
        content: formattedContent
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '保存方案失败')
    }

    ElMessage.success('保存方案成功')
    templateFormVisible.value = false
    cartVisible.value = false
    clearCart()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存方案失败')
  }
}

// 复制提示词到剪贴板
const copyPrompts = () => {
  const formattedPrompts = cartItems.value.map(item => item.original_text).join(', ') + ','
  navigator.clipboard.writeText(formattedPrompts)
    .then(() => {
      ElMessage.success('已复制到剪贴板')
    })
    .catch(() => {
      ElMessage.error('复制失败，请重试')
    })
}

// 购物车相关方法
const toggleCart = () => {
  cartVisible.value = !cartVisible.value
}
</script>

<template>
  <el-container class="prompt-manage">
    <!-- 左侧分类树 -->
    <el-aside width="250px" class="category-aside">
      <div class="category-header">
        <h3>分类管理</h3>
        <el-tooltip content="新建分类" placement="top">
          <el-button type="primary" :icon="Plus" circle @click="openCreateForm" />
        </el-tooltip>
      </div>
      <el-tree :data="categories" node-key="id" :props="{
        label: 'name',
        children: 'children'
      }" @node-click="handleCategorySelect" default-expand-all>
        <template #default="{ node, data }">
          <div class="custom-tree-node">
            <span>{{ node.label }}</span>
            <span v-if="!data.is_default" class="actions">
              <el-tooltip content="编辑分类" placement="top">
                <el-button :icon="Edit" circle link @click.stop="openEditForm(data)" />
              </el-tooltip>
              <el-tooltip content="删除分类" placement="top">
                <el-button :icon="Delete" circle link type="danger" @click.stop="deleteCategory(data.id)" />
              </el-tooltip>
            </span>
          </div>
        </template>
      </el-tree>
    </el-aside>

    <!-- 右侧提示词列表 -->
    <el-main class="prompt-main" @scroll="handleScroll">
      <!-- 顶部操作栏 -->
      <div class="prompt-header">
        <div class="category-filter">
          <span>当前分类：</span>
          <el-tag v-if="!selectedCategory" type="info">全部分类</el-tag>
          <el-tag v-else type="success" closable @close="handleCategorySelect(null)">
            {{ selectedCategory.name }}
          </el-tag>
        </div>
        <el-input
          v-model="searchQuery"
          placeholder="搜索提示词..."
          class="search-input"
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" :icon="Plus" @click="openCreatePromptForm">添加提示词</el-button>
      </div>

      <!-- 提示词列表 -->
      <div class="prompt-list">
        <el-card v-for="prompt in prompts" :key="prompt.id" class="prompt-card">
          <div class="prompt-content">
            <div class="prompt-text">{{ prompt.original_text }}</div>
            <div class="prompt-translation">{{ prompt.chinese_translation }}</div>
            <div class="prompt-category">
              <el-tag v-for="(cat, index) in prompt.categoryPath" :key="index" size="small"
                :type="index === 0 ? '' : 'info'">
                {{ cat }}
              </el-tag>
            </div>
          </div>
          <div class="prompt-actions">
            <el-button :icon="ShoppingCart" circle @click="addToCart(prompt)" />
            <el-button :icon="Edit" circle @click="openEditPromptForm(prompt)" />
            <el-button :icon="Delete" circle type="danger" @click="deletePrompt(prompt.id)" />
          </div>
        </el-card>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-more">
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
          <span>加载中...</span>
        </div>
      </div>

      <!-- 提示词表单弹窗 -->
      <el-dialog v-model="promptFormVisible" :title="isEditingPrompt ? '编辑提示词' : '添加提示词'" width="500px">
        <el-form :model="promptForm" label-width="100px">
          <el-form-item label="提示词原文" required>
            <el-input v-model="promptForm.original_text" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="中文翻译">
            <el-input v-model="promptForm.chinese_translation" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="所属分类" required>
            <el-tree-select v-model="promptForm.category_id" :data="categories" :props="{
              value: 'id',
              label: 'name',
              children: 'children'
            }" check-strictly />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="promptFormVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePromptSubmit">确定</el-button>
        </template>
      </el-dialog>
    </el-main>

    <!-- 购物车按钮 -->
    <div class="cart-button" @click="toggleCart">
      <el-badge :value="cartItems.length" :hidden="!cartItems.length">
        <el-button :icon="ShoppingCart" circle type="primary" size="large" />
      </el-badge>
    </div>

    <!-- 购物车抽屉 -->
    <el-drawer v-model="cartVisible" title="购物车" direction="rtl" size="400px">
      <template #default>
        <div class="cart-content">
          <el-alert
            title="提示"
            type="info"
            :closable="false"
            show-icon>
            点击提示词可移除，点击保存按钮可保存当前方案
          </el-alert>
          
          <div class="cart-list" v-if="cartItems.length > 0">
            <div class="cart-actions">
              <el-button type="primary" @click="copyPrompts" :icon="DocumentCopy">
                复制提示词
              </el-button>
            </div>
            <div class="cart-section">
              <div class="section-title">提示词原文</div>
              <div class="tags-container">
                <el-tag
                  v-for="(item, index) in cartItems"
                  :key="index"
                  closable
                  @close="removeFromCart(item.original_text)"
                  class="cart-tag">
                  {{ item.original_text }}
                </el-tag>
              </div>
            </div>
            <div class="cart-section">
              <div class="section-title">中文翻译</div>
              <div class="tags-container">
                <el-tag
                  v-for="(item, index) in cartItems"
                  :key="index"
                  type="info"
                  class="cart-tag-translation">
                  {{ item.chinese_translation }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-cart">
            <el-empty description="购物车为空" />
          </div>
        </div>
      </template>
      <template #footer>
        <div class="cart-footer">
          <el-button @click="clearCart">清空购物车</el-button>
          <el-button type="primary" @click="saveAsPlan">保存为方案</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 保存方案弹窗 -->
    <el-dialog v-model="templateFormVisible" title="保存方案" width="400px">
      <el-form :model="templateForm" label-width="80px">
        <el-form-item label="方案名称">
          <el-input v-model="templateForm.name" placeholder="请输入方案名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateFormVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 分类表单弹窗 -->
    <el-dialog v-model="categoryFormVisible" :title="isEditing ? '编辑分类' : '新建分类'" width="30%">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父级分类">
          <el-tree-select v-model="categoryForm.parent_id" :data="categories" :props="{
            label: 'name',
            children: 'children',
            value: 'id'
          }" placeholder="请选择父级分类" clearable check-strictly />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="categoryFormVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCategorySubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<style scoped>
.prompt-manage {
  height: 100%;
}

.category-aside {
  border-right: 1px solid #dcdfe6;
  padding: 20px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
}

.prompt-main {
  padding: 20px;
}

.prompt-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;  
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
}

.category-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
}

.prompt-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.prompt-card {
  display: flex;
  flex-direction: column;
}

.prompt-content {
  flex: 1;
}

.prompt-text {
  font-size: 16px;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prompt-translation {
  color: #666;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cart-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 500;
  margin-bottom: 10px;
  color: #303133;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cart-tag-translation {
  margin-top: 8px;
}

.prompt-category {
  margin-bottom: 12px;

  .el-tag {
    margin-right: 8px;
  }
}

.prompt-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.cart-button {
  position: fixed;
  right: 40px;
  bottom: 40px;
  z-index: 100;
}

.cart-content {
  min-height: 200px;
}

.cart-footer {
  text-align: right;
}

.actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.custom-tree-node:hover .actions {
  opacity: 1;
}

.dialog-footer {
  text-align: right;
}
</style>