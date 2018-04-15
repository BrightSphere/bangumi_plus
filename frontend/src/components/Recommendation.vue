<template>
  <div id="recommendation">

    <mu-flexbox>

      <mu-flexbox-item>
        <a :href="'/subject/'+subject_1.id">
        <mu-card>
          <mu-card-title :title="subject_1.main_name" :subTitle="subject_1.name"/>
        </mu-card>
          </a>
      </mu-flexbox-item>

      <mu-flexbox-item>
        <a :href="'/subject/'+subject_2.id">
        <mu-card>
          <mu-card-title :title="subject_2.main_name" :subTitle="subject_2.name"/>
        </mu-card>
        </a>
      </mu-flexbox-item>

    </mu-flexbox>
    <br/>
    <mu-card v-for="comment in comments" style="margin-top: 10px">
      <mu-card-header :title="comment.user.nickname">
        <mu-avatar :src="comment.user.avatar" slot="avatar"/>
      </mu-card-header>
      <mu-card-text>
        <pre>{{ comment.comment }}</pre>
      </mu-card-text>
      <mu-card-actions v-if="comment.is_author">
        <mu-flat-button label="编辑" :href="`/comment/${comment.id}`" primary/>
      </mu-card-actions>
    </mu-card>
    <br/>
    <mu-raised-button v-if="!haveComment" label="创建推荐" :href="createHref" fullWidth primary/>
  </div>
</template>

<script>
  export default {
    name: 'Recommendation',
    data() {
      return {
        subject_1: {},
        subject_2: {},
        comments: []
      }
    },
    computed: {
      haveComment: function () {
        for( let comment of this.comments){
          if (comment.is_author){
            return true
          }
        }
        return false
      },
      createHref: function () {
        return decodeURIComponent(`/create?subject_1=${this.subject_1.id}&subject_2=${this.subject_2.id}`)
      }
    },
    mounted: function () {
      const self = this
      this.axios
        .get(`/recommendations/${this.$route.params.key}/`)
        .then(function (response) {
          console.log(response)
          self.subject_1 = response.data.subject_smaller
          self.subject_2 = response.data.subject_bigger
          self.comments = response.data.comments
          document.title = `${self.subject_1.main_name} - ${self.subject_2.main_name}`
        })
        .catch(function (error) {
          console.log(error)
        })
    },
    methods: {
      have_comment(){
        return 1
      }
    }
  }
</script>
