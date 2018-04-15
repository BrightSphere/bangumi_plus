<template>
  <div>
    <mu-dialog :open="!!dialog" title="提交失败">
      {{ dialog }}
      <mu-flat-button label="确定" slot="actions" primary @click="close"/>
    </mu-dialog>
    <mu-card>
      <mu-card-title title="关联推荐"/>
      <div style="margin: 10px">
        <mu-text-field label="条目1 ID" labelFloat type="number" v-model="subject_1"/>
        <mu-text-field label="条目2 ID" labelFloat type="number" v-model="subject_2"/>
        <mu-text-field label="推荐理由" labelFloat hintText="请勿推荐作品的续集或前传" v-model="comment" multiLine :rows="10"
                       fullWidth/>
      </div>
      <mu-card-actions>
        <mu-flat-button label="提交" @click="submit" fullWidth primary/>
      </mu-card-actions>
    </mu-card>
  </div>
</template>

<script>

  export default {
    name: 'CommentCreate',
    data() {
      return {
        subject_1: null,
        subject_2: null,
        comment: null,
        dialog: null
      }
    },
    methods: {
      submit() {
        const self = this
        this.axios.post(`/comments/`,
          {
            subject_1: this.subject_1,
            subject_2: this.subject_2,
            comment: this.comment
          }).then(function (response) {
          console.log('got comment detail!', response)
          self.$router.push(`/recommendation/${response.data.recommendation}`)
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
      document.title = "创建推荐"
      this.subject_1 = this.$route.query.subject_1
      this.subject_2 = this.$route.query.subject_2
    }
  }
</script>
