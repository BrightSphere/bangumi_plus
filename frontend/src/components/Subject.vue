<template>
  <div v-if="subject">
    <mu-card class="title-card">
      <mu-card-title :title="subject.main_name" :subTitle="subject.name"/>
      <mu-card-actions>
        <mu-raised-button label="返回主站" class="main-button" primary :href="subjectUrl"/>
      </mu-card-actions>
    </mu-card>

    <br/>
    <mu-card>
      <mu-card-title title="推荐的条目"/>
      <div class="gridlist-container">
        <mu-grid-list class="gridlist-inline">
          <mu-grid-tile
            v-for="recommendation in subject.recommendations"
            :key="recommendation.key"
            @click.native="to_recommendation(recommendation.key)"
          >
            <img :src="recommendation.subject.cover"/>
            <span slot="title">{{recommendation.subject.main_name}}</span>
            <span slot="subTitle"><b>{{to_recommendation_info(recommendation)}}</b></span>
          </mu-grid-tile>
          <mu-grid-tile @click.native="to_create_comment">
            <img src="../assets/logo.png"/>
            <span slot="title">新建推荐</span>
            <span slot="subTitle"><b>关联条目</b></span>
          </mu-grid-tile>
        </mu-grid-list>
      </div>
    </mu-card>
  </div>
  <div v-else>
    <mu-card class="title-card">
      <mu-card-title title="载入中..." subTitle="稍等试试"/>
    </mu-card>
  </div>
</template>

<script>
  export default {
    name: 'Subject',
    data() {
      return {
        subject: null
      }
    },
    computed: {
      subjectUrl: function () {
        return `//bgm.tv/subject/${this.subject.id}`
      }
    },
    created: function () {
      const self = this
      this.axios.get(`/subjects/${this.$route.params.id}/`)
        .then(function (response) {
          console.log('got subject detail!', response)
          self.subject = response.data
          document.title = self.subject.main_name
        }).catch(function (error) {
        console.log('error when getting subject detail', error)
        self.$router.push("/?type=timeout")
      })
    },
    methods: {
      to_recommendation_info(recommendation) {
        if (recommendation.auto) {
          return `相似度${recommendation.similarity}%`
        }
        else {
          return `${recommendation.count}人推荐`
        }
      },
      to_recommendation(key) {
        let redirect = decodeURIComponent(`/recommendation/${key}`)
        this.$router.push(redirect)
      },
      to_create_comment() {
        let redirect = decodeURIComponent(`/create?subject_1=${this.subject.id}`)
        this.$router.push(redirect)
      }
    }
  }
</script>

<style>
  .gridlist-container {
    display: flex;
    flex-wrap: wrap;
    padding: 16px;
  }

  .gridlist-inline {
    display: flex;
    flex-wrap: nowrap !important;
    overflow-x: auto;
  }
</style>
