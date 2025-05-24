import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/prompts'
    },
    {
      path: '/prompts',
      name: 'prompts',
      component: () => import('@/views/PromptManage.vue')
    },
    {
      path: '/templates',
      name: 'templates',
      component: () => import('../views/TemplateManage.vue')
    }
  ]
})

export default router
