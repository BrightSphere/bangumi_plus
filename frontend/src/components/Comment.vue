<template>
  <div v-if="comment">
    <mu-dialog :open="!!dialog" title="提交失败">
      {{ dialog }}
      <mu-flat-button label="确定" slot="actions" primary @click="close"/>
    </mu-dialog>
    <mu-card>
      <mu-card-title title="推荐详情"/>
      <div style="margin: 10px">
        <mu-text-field label="推荐理由" labelFloat hintText="请勿推荐作品的续集或前传" v-model="comment.comment"
                       multiLine :rows="10" :disabled="!isAuthor"
                       fullWidth/>
      </div>
      <mu-card-actions v-if="isAuthor">
        <mu-flat-button label="提交" @click="submit" primary/>
        <mu-raised-button label="删除" @click="delete_comment" primary/>
      </mu-card-actions>
    </mu-card>
  </div>
</template>

<script>

  export default {
    name: 'Comment',
    data() {
      return {
        comment: null,
        isAuthor: false,
        dialog: null
      }
    },
    methods: {
      submit() {
        const self = this
        this.axios.put(`/comments/${this.comment.id}/`,
          {
            comment: this.comment.comment
          }).then(function (response) {
          console.log('got comment detail!', response)
          self.$router.push(`/recommendation/${response.data.recommendation}`)
        }).catch(function (error) {
          console.log('error when getting comment detail', error)
          self.open(error)
        })
      },
      delete_comment() {
        const self = this
        this.axios.delete(`/comments/${this.comment.id}/`)
          .then(function (response) {
          console.log('got comment detail!', response)
          self.$router.push('/')
        }).catch(function (error) {
          console.log('error when getting comment detail', error)
          self.open(error)
        })
      },
      open(content) {
        this.dialog = content
      },
      close() {
        this.dialog = null
      }
    },
    created: function () {
      const self = this
      this.axios.put(`/comments/${this.$route.params.id}/`)
        .then(function (response) {
          console.log('got comment detail!', response)
          self.comment = response.data
          self.isAuthor = response.data.is_author
        }).catch(function (error) {
          console.log('error when getting comment detail', error)
          self.open(error)
        })
    }
  }
</script>
