<template>
  <q-layout view="lHh lPr lFf" color="dark">
    <q-toolbar color="dark">
      <q-btn
        v-if="image != ''"
        flat round dense
        icon="arrow_back"
        @click="image = ''"
      />
      <q-toolbar-title>
        Fospex
      </q-toolbar-title>
    </q-toolbar>
    <q-page-container>
      <q-page class="flex flex-center" :padding="true">
        <q-card color="dark">
          <q-card-main v-if="image == ''">
            <q-uploader v-model="imageURL" :auto-expand="false" :url="imageURL" :hide-upload-button="true" @add="initImage"  color="dark" />
          </q-card-main>
        </q-card>
        <div v-if="!showModified" class="col-lg-9 col-md-8">
          <img :src="image" />
        </div>
        <div class="col-lg-9 col-md-8" v-if="showModified">
          <img :src="imageResult" />
        </div>
        <q-inner-loading :visible="loadMod" dark></q-inner-loading>
        <q-modal v-model="spectrumOpened" no-backdrop-dismiss  :content-css="{minWidth: '80vw', minHeight: '80vh'}" :content-class="dark" dark>
          <q-modal-layout dark>
            <q-toolbar slot="header">
              <q-toolbar-title>
                Image spectrum
              </q-toolbar-title>
              <q-btn
                flat
                round
                dense
                v-close-overlay
                @click="spectrumOpened = false"
                icon="close"
              />
            </q-toolbar>
            <div class="layout-padding">
              <img :src="spectrumImage" class="full-height" />
            </div>
          </q-modal-layout>
        </q-modal>
      </q-page>
    </q-page-container>
    <q-layout-drawer side="right" v-model="dummy" id="inspector">
      <q-list no-border color="dark" dark>
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
                  ]"
                />
              </q-item>
              <q-item-separator />
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
                  disabled
                />
              </q-item>
              <q-item-separator />
              <q-list-header>Smoothing</q-list-header>
              <q-item>
                <q-slider v-model="sigma" :min="1" :max="100" label-always :step="1" />
              </q-item>
            </q-list>
          </div>
        </q-collapsible>
        <q-item-separator />
      </q-list>
      <q-inner-loading :visible="loadInit" dark></q-inner-loading>
    </q-layout-drawer>
  </q-layout>
</template>

<style lang="stylus">
@import '~variables'
#inspector
  background: #303030
#zoomIn
  position: absolute
  right: 10px
  bottom: 10px
</style>

<script>

import {
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
  QModal,
  QModalLayout,
  QInnerLoading,
  QSpinnerGears
} from 'quasar'
import axios from 'axios'
import vueDropzone from 'vue2-dropzone'

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
    vueDropzone,
    QModal,
    QModalLayout,
    QInnerLoading,
    QSpinnerGears
  },
  data () {
    return {
      progId: 0,
      image: '',
      imageURL: '',
      spectrumImage: '',
      imageResult: '',
      frequencyThreshold: {
        min: 0,
        max: 100
      },
      kernelThresholds: {
        min: 0,
        max: 100
      },
      filterType: 'bandpass',
      mode: 'magnitude',
      filterForm: 'circle',
      isGaussian: false,
      enableFilter: false,
      sigma: 5,
      notchFilterPositions: [],
      showModified: true,
      dropOptions: {
        url: ''
      },
      spectrumOpened: false,
      windowingMethod: '',
      loadInit: false,
      loadMod: false,
      dummy: true
    }
  },
  name: 'FourierSpectrumExplorer',
  watch: {
    spectrumImage () {
      console.log('Spectrum image has been modified')
    },
    frequencyThreshold () {
      console.log('Filter thresholds have been modified')
      this.getModSpectrum()
    },
    kernelThresholds () {
      console.log('Filter thresholds have been modified')
      this.getModSpectrum()
    },
    filterType () {
      console.log('Filter method have been modified')
      this.getModSpectrum()
    }
  },
  methods: {
    getModSpectrum () {
      this.loadMod = true
      axios.post(`http://localhost:5000/filter/`, {
        val_low: this.kernelThresholds.min,
        val_high: this.kernelThresholds.max,
        freq_low: this.frequencyThreshold.min,
        freq_high: this.frequencyThreshold.max,
        progId: this.progId,
        filter_type: this.filterType
      })
        .then(response => {
          // JSON responses are automatically parsed.
          this.spectrumImage = response.data['spectrumImage']
          this.imageResult = response.data['imageResult']
          this.loadMod = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    initImage (event) {
      // Convert to base64 code
      let file = event[0]
      let imgBase64 = ''
      let reader = new FileReader()
      this.loadInit = true
      reader.readAsDataURL(file)

      reader.onload = function () {
        imgBase64 = reader.result.toString('base64')
        this.image = imgBase64

        let valLow = this.kernelThresholds.min
        let valHigh = this.kernelThresholds.max

        let freqLow = this.frequencyThreshold.min
        let freqHigh = this.frequencyThreshold.max

        if (!this.enableFilter) {
          freqLow = 0
          freqHigh = 1000000
          valLow = 0
          valHigh = 1000000
        }

        let filterType = this.filterType

        console.log(reader.result.toString('base64'))
        console.log('Sent:')
        console.log(imgBase64)

        // let imgBase64 = event[0]['__img']['currentSrc'].split('base64,')[1]
        // Post to API
        axios.post(`http://localhost:5000/`, {
          image: imgBase64,
          val_low: valLow,
          val_high: valHigh,
          freq_low: freqLow,
          freq_high: freqHigh,
          filter_type: filterType
        })
          .then(response => {
            // JSON responses are automatically parsed.
            // this.spectrumImage = 'data:image/png;base64,' + response.data['image']
            this.spectrumImage = response.data['spectrumImage']
            this.imageResult = response.data['imageResult']
            this.progId = response.data['progId']

            this.loadInit = false
            console.log('Response:')
            console.log(this.spectrumImage)
          })
          .catch(e => {
          })
      }.bind(this)
      reader.onerror = function (error) {
        console.log('Error: ', error)
      }
      this.imageURL = ''
      console.log('Prog Id: ' + this.progId)
    }
  }
}
</script>
