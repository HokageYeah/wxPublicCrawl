import { createRouter, createWebHistory } from 'vue-router'
import WeChatLogin from '../views/WeChatLogin.vue'
import SearchPublic from '../views/SearchPublic.vue'
import ArticleList from '../views/ArticleList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: WeChatLogin
    },
    {
      path: '/search',
      name: 'search',
      component: SearchPublic
    },
    {
      path: '/articles',
      name: 'articles',
      component: ArticleList
    }
  ]
})

export default router
