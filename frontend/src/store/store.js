import Vuex from 'vuex'
import Vue from 'vue'
import * as types from './types'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token'),
    redirect_url: localStorage.getItem("redirect_url")
  },
  mutations: {
    [types.LOGIN]: (state, data) => {
      localStorage.token = data
      state.token = data
    },
    [types.LOGOUT]: (state) => {
      localStorage.removeItem('token')
      state.token = null
    },
    [types.SAVE]: (state, data) => {
      localStorage.redirect_url = data
      state.redirect_url = data
    },
    [types.REMOVE]: (state) => {
      localStorage.removeItem('redirect_url')
      state.redirect_url = null
    }
  }
})
