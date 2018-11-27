<template>
  <q-list no-border color="dark">
    <q-item>
      <q-btn-toggle
        v-model="showModified"
        toggle-color="primary"
        :options="[
          {label: 'Show original', value: false},
          {label: 'Show modified', value: true},
        ]"
      />
    </q-item>
    <q-item-separator />
    <q-collapsible icon="explore" label="Image spectrum">
      <div>
        <q-list no-border color="dark">
          <q-item>
            <img :src="spectrumImage" class="full-width" />
            <q-btn
              outline
              round
              icon="zoom_in"
              color="primary"
              @click="spectrumOpened = true"
              id="zoomIn"
            >
            </q-btn>
          </q-item>
          <q-list-header>Filter kernel thresholds (in %)</q-list-header>
          <q-item>
            <q-range :value="kernelThresholds" @change="val => {kernelThresholds = val}" :min="0" :max="100" label-always :step="1" />
          </q-item>
          <q-list-header>Filter type</q-list-header>
          <q-item>
            <q-btn-toggle
              v-model="filterType"
              toggle-color="primary"
              :options="[
                {label: 'Bandpass', value: 'bandpass'},
                {label: 'Band reject', value: 'bandreject'},
              ]" disable
            />
          </q-item>
          <q-list-header>Windowing method</q-list-header>
          <q-item>
            <q-btn-toggle
              v-model="windowingMethod"
              toggle-color="primary"
              :options="[
                {label: 'None', value: ''},
                {label: 'Hanning window', value: 'hanning'},
                {label: 'Parzel window', value: 'parzel'},
              ]"
              disable
            />
          </q-item>
          <q-item>
            <q-item-main>
              <q-item-tile label>Smoothing</q-item-tile>
            </q-item-main>
            <q-item-side right>
              <q-toggle v-model="isGaussian" disable />
            </q-item-side>
          </q-item>
          <q-item v-show="isGaussian">
            <q-slider v-model="sigma" v-show="isGaussian" :min="1" :max="100" label-always :step="1" disable />
          </q-item>
        </q-list>
      </div>
    </q-collapsible>
    <q-item-separator />
  </q-list>
</template>

<script>
import {
  QRange,
  QSlider,
  QCard,
  QCardMedia,
  QCardSeparator,
  QCardActions,
  QToggle,
  QBtnToggle,
  QList,
  QListHeader,
  QItem,
  QItemMain,
  QItemSeparator,
  QItemSide,
  QItemTile,
  QCollapsible,
} from 'quasar'

export default {
  components: {
    QRange,
    QSlider,
    QUploader,
    QCard,
    QCardMedia,
    QCardTitle,
    QCardMain,
    QCardSeparator,
    QCardActions,
    QToggle,
    QBtnToggle,
    QList,
    QListHeader,
    QItem,
    QItemMain,
    QItemSeparator,
    QItemSide,
    QItemTile,
    QCollapsible,
    QInnerLoading,
    QSpinnerGears,
    Inspector
  },
  // name: 'ComponentName',
  data () {
    return {}
  }
}
</script>

<style>
</style>
