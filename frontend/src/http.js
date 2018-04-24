import axios from 'axios'
import store from './store/store'
// import * as types from './store/types'
import router from './router'

// axios 配置
axios.defaults.timeout = 20000
axios.defaults.baseURL = '/api/'
// axios.defaults.xsrfCookieName = 'csrftoken'
// axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// http request 拦截器
axios.interceptors.request.use(
  config => {
    if (store.state.token) {
      config.headers.Authorization = 'Token ' + store.state.token
    }
    return config
  },
  err => {
    return Promise.reject(err)
  })

axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 500:
        case 404:
        case 401:
        case 403:
          router.replace({
            path: `/?type=${error.response.status}`
          })
      }
    }
    return Promise.reject(error.response.data)
  })

export default axios
