<template>
  <div class="api-page-grid">
    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('apiAccess.title') }}</h3>
          <p class="panel-desc">{{ t('apiAccess.desc') }}</p>
        </div>
      </div>

      <div class="summary-list">
        <div class="summary-item">
          <span>{{ t('apiAccess.currentAddress') }}</span>
          <strong>{{ apiInfo?.current_base_url || '—' }}</strong>
        </div>
        <div class="summary-item">
          <span>{{ t('apiAccess.backendAddress') }}</span>
          <strong>{{ apiInfo?.backend_mode?.base_url || t('apiAccess.backendStopped') }}</strong>
        </div>
        <div class="summary-item">
          <span>{{ t('apiAccess.apiKey') }}</span>
          <strong class="api-key-text">{{ apiInfo?.api_key || '—' }}</strong>
        </div>
      </div>

      <div class="action-row" style="margin-top: 16px">
        <el-button type="primary" @click="copyText(apiInfo?.current_base_url)">
          {{ t('apiAccess.copyAddress') }}
        </el-button>
        <el-button plain :loading="regenerating" @click="handleRegenerate">
          {{ t('apiAccess.regenerateKey') }}
        </el-button>
        <el-button plain @click="copyText(apiInfo?.api_key)">
          {{ t('apiAccess.copyKey') }}
        </el-button>
      </div>
    </div>

    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('apiAccess.exampleTitle') }}</h3>
          <p class="panel-desc">{{ t('apiAccess.exampleDesc') }}</p>
        </div>
      </div>

      <div class="code-block">{{ profileListExample }}</div>
      <div class="code-block">{{ startProfileExample }}</div>
      <div class="form-tip">{{ t('apiAccess.docTip') }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useProfileStore } from '../stores/profile.js'

const { t } = useI18n()
const store = useProfileStore()
const regenerating = ref(false)

const apiInfo = computed(() => store.apiInfo)

const profileListExample = computed(() => {
  const baseUrl = apiInfo.value?.current_base_url || 'http://127.0.0.1:8000/open-api'
  const apiKey = apiInfo.value?.api_key || 'YOUR_API_KEY'
  return `curl -H "X-API-Key: ${apiKey}" "${baseUrl}/profiles"`
})

const startProfileExample = computed(() => {
  const baseUrl = apiInfo.value?.current_base_url || 'http://127.0.0.1:8000/open-api'
  const apiKey = apiInfo.value?.api_key || 'YOUR_API_KEY'
  return `curl -X POST -H "X-API-Key: ${apiKey}" "${baseUrl}/profiles/PROFILE_ID/start"`
})

onMounted(async () => {
  if (!store.apiInfo) {
    await store.refreshApiInfo()
  }
})

async function handleRegenerate() {
  regenerating.value = true
  try {
    await store.regenerateApiKey()
    ElMessage.success(t('apiAccess.keyRegenerated'))
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    regenerating.value = false
  }
}

async function copyText(value) {
  if (!value) return
  try {
    await navigator.clipboard.writeText(value)
    ElMessage.success(t('apiAccess.copied'))
  } catch (error) {
    ElMessage.error(error.message || t('common.loadFailed'))
  }
}
</script>
