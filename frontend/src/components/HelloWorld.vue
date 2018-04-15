<template>
  <div class="hello">
    <mu-card>
      <mu-card-title title="欢迎使用Bangumi互助推荐"/>
      <mu-card-text>
        <pre>{{ text }}</pre>
      </mu-card-text>
      <mu-card-actions>
        <mu-text-field hintText="Subject ID" type="number" v-model="id" fullWidth/>
        <br/>
        <mu-flat-button :href="`/subject/${id}`" label="GO" fullWidth/>
      </mu-card-actions>
    </mu-card>
  </div>
</template>

<script>

  export default {
    name: 'HelloWorld',
    data() {
      return {
        id: null,
        code: 200
      }
    },
    computed: {
      text: function () {
        if (!this.code) {
          return '但这个页面没什么用...\n' +
            '使用subject/:id来访问某一条目的推荐内容。'
        }
        switch (String(this.code)) {
          case '404':
            return '小伙子你刚刚似乎走错地方了。'
          case '401':
            return '请尝试登录。'
          case '403':
            return '无权限。'
          default:
            return '似乎产生了一些问题，换个页面试试。'
        }
      }
    },
    created: function () {
      this.code = this.$route.query.type
      console.log(this.code)
    }
  }
</script>
