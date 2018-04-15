import Vue from 'vue'
import Router from 'vue-router'
import Subject from '@/components/Subject'
import Recommendation from '@/components/Recommendation'
import Comment from '@/components/Comment'
import CommentCreate from '@/components/CommentCreate'
import Auth from '@/components/Auth'
import HelloWorld from '@/components/HelloWorld'
import store from '@/store/store'

Vue.use(Router)

const routes_config = {
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/subject/:id',
      name: 'Subject',
      component: Subject
    },
    {
      path: '/recommendation/:key',
      name: 'Recommendation',
      component: Recommendation
    },
    {
      path: '/comment/:id',
      name: 'Comment',
      component: Comment,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/create',
      name: 'CommentCreate',
      component: CommentCreate,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/auth/',
      name: 'Auth',
      component: Auth
    },
    {
      path: "*",
      redirect: "/"
    }
  ]
}

const router = new Router(routes_config)

router.beforeEach((to, from, next) => {
  if (to.meta.requireAuth) {  // 判断该路由是否需要登录权限
    if (store.state.token) {  // 通过vuex state获取当前的token是否存在
      next()
    }
    else {
      next({
        path: '/',
        query: {type: 401}  // 将跳转的路由path作为参数，登录成功后跳转到该路由
      })
    }
  }
  else {
    next()
  }
})

export default router
