<template>
  <mu-card>
    <mu-card-title title="授权中"/>
    <mu-card-text>
      可能需要一些时间...
    </mu-card-text>
  </mu-card>
</template>

<script>
  export default {
    name: 'Auth',
    created: function () {
      document.title = "授权中..."
      if (this.$route.query.code) {
        this.axios
          .get(`/token/?code=${this.$route.query.code}`)
          .then(function (response) {
            console.log(response)
            this.$emit('login', response.data)
            this.redirect()
          }.bind(this))
          .catch(function (error) {
            console.log(error)
            this.redirect()
          }.bind(this))
      }
      else {
        this.redirect()
      }
    },
    methods: {
      redirect() {
        let redirect = this.$store.state.redirect_url
        this.$store.commit('remove')
        this.$router.push({
          path: redirect ? redirect : '/'
        })
      }
    }
  }
</script>
