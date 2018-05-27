<template>
  <q-page class="flex flex-center" :padding="true">
    <div class="row gutter-sm full-width full-height" id="fourier">
      <div class="col-md-4 col-s-12">
        <q-card class="">
          <q-card-title>
            Input image
          </q-card-title>
          <q-card-media>
            <img :src="image" />
          </q-card-media>
          <q-card-main>
            <q-uploader v-model="imageURL" :auto-expand="false" :url="imageURL" :hide-upload-button="true" @add="initImage" />
          </q-card-main>
        </q-card>
      </div>
      <div class="col-md-4 col-s-12">
        <q-card class="">
          <q-card-title>
            Amplitude spectrum
          </q-card-title>
          <q-card-media>
            <img :src="spectrumImage" />
          </q-card-media>
          <q-card-main>
            <div class="row block gutter-s full-width">
              <div class="col">
                Frequency thresholds
                <q-range :value="filterThreshold" @change="val => {filterThreshold = val}" :min="0" :max="255" label-always :step="1" />
              </div>
              <div class="col">
                <q-toggle v-model="inverseFilter" color="teal-8" label="Inverse filter" />
              </div>
              <div class="col">
                <q-toggle v-model="isGaussian" color="teal-8" label="Filter with Gaussian" />
                <p v-show="isGaussian">Gaussian sigma value</p>
                <q-slider v-model="sigma" v-show="isGaussian" :min="1" :max="100" label-always :step="1" />
              </div>
            </div>
          </q-card-main>
        </q-card>
      </div>
      <div class="col-md-4 col-s-12">
        <q-card class="">
          <q-card-title>
            Output image
          </q-card-title>
          <q-card-media>
            <img :src="imageResult" />
          </q-card-media>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style>
</style>

<script>

import {QRange, QSlider, QUploader, QCard, QCardMedia, QCardTitle, QCardMain, QCardSeparator, QCardActions, QToggle} from 'quasar'
import axios from 'axios'

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
    QToggle
  },
  data () {
    return {
      progId: 0,
      image: '',
      imageURL: '',
      spectrumImage: '',
      imageResult: '',
      filterThreshold: {
        min: 0,
        max: 255
      },
      inverseFilter: false,
      mode: 'magnitude',
      filterForm: 'circle',
      isGaussian: false,
      sigma: 5,
      notchFilterPositions: []
    }
  },
  name: 'FourierSpectrumExplorer',
  watch: {
    spectrumImage () {
      console.log('Spectrum image has been modified')
    },
    filterThreshold () {
      console.log('Filter thresholds have been modified')
      this.getModSpectrum()
    }
  },
  methods: {
    getModSpectrum () {
      axios.post(`http://localhost:5000/filter/`, {
        low: this.filterThreshold.min,
        high: this.filterThreshold.max,
        progId: this.progId
      })
        .then(response => {
          // JSON responses are automatically parsed.
          this.spectrumImage = response.data['spectrumImage']
          this.imageResult = response.data['imageResult']
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
      reader.readAsDataURL(file)

      reader.onload = function () {
        imgBase64 = reader.result.toString('base64')
        this.image = imgBase64

        let low = this.filterThreshold.min
        let high = this.filterThreshold.max

        console.log(reader.result.toString('base64'))
        console.log('Sent:')
        console.log(imgBase64)

        // let imgBase64 = event[0]['__img']['currentSrc'].split('base64,')[1]
        // Post to API
        axios.post(`http://localhost:5000/`, {
          image: imgBase64,
          low: low,
          high: high
        })
          .then(response => {
            // JSON responses are automatically parsed.
            // this.spectrumImage = 'data:image/png;base64,' + response.data['image']
            this.spectrumImage = response.data['spectrumImage']
            this.imageResult = response.data['imageResult']
            this.progId = response.data['progId']
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
    }
  }
}
</script>
