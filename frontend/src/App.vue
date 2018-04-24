<template>
  <div id="app">
    <div class="layout">
      <div class="header">
        <mu-appbar :title="username">
          <mu-avatar slot="left" :src="avatar"/>
          <mu-flat-button v-if="user" v-on:click="logout" color="white" label="注销" slot="right"/>
          <mu-flat-button v-else color="white" label="授权登录" @click="to_bangumi" slot="right"/>
        </mu-appbar>
      </div>
      <div class="content">
        <router-view v-on:login="login"/>
      </div>
      <div class="footer">
        Bangumi Plus ©2018
      </div>
    </div>
  </div>
</template>

<script>
  import defaultImage from './assets/logo.png'
  import * as types from './store/types'

  export default {
    name: 'App',
    data: function () {
      return {
        user: null
      }
    },
    computed: {
      username: function () {
        return this.user ? this.user.nickname : ``
      },
      avatar: function () {
        return this.user ? this.user.avatar : defaultImage
      },
      redirect_url: function () {
        return 'https://bgm.tv/oauth/authorize?client_id=bgm265a93901259d1d&response_type=code'
      }
    },
    created: function () {
      if (this.$store.state.token) {
        this.refreshUser()
      }
    },
    methods: {
      logout() {
        const self = this
        self.user = null
        this.$store.commit(types.LOGOUT)
        location.reload()
      },
      refreshUser() {
        const self = this
        this.axios
          .get('/user/')
          .then(function (response) {
            console.log(response)
            self.user = response.data
          })
          .catch(function (error) {
            console.log(error)
          })
      },
      to_bangumi() {
        this.$store.commit(types.SAVE, this.$route.path)
        window.location.href = this.redirect_url
      },
      login(payload) {
        this.$store.commit(types.LOGIN, payload.token)
        this.refreshUser()
      }
    }
  }
</script>
<style>
  .content {
    width: 90%;
    margin: 10px auto;
  }

  .footer {
    padding: 20px 0;
    text-align: center;
  }
</style>
