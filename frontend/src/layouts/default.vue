<template>
  <router-view />
</template>

<script>
import { openURL } from 'quasar'

export default {
  name: 'LayoutDefault',
  data () {
    return {
      leftDrawerOpen: this.$q.platform.is.desktop
    }
  },
  methods: {
    openURL
  }
}
</script>

<style lang="stylus">
@import '~variables'
body
  background: $body-bg

.bg-primary
  color: black !important
</style>
