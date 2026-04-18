<template>
  <div class="settings-stack">
    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('settings.generalTitle') }}</h3>
          <p class="panel-desc">{{ t('settings.generalDesc') }}</p>
        </div>
      </div>

      <el-form label-position="top">
        <el-form-item :label="t('settings.userDataRoot')">
          <el-input v-model="form.user_data_root" :placeholder="t('settings.userDataRootPlaceholder')" />
          <div class="form-tip">{{ t('settings.userDataRootTip') }}</div>
        </el-form-item>
      </el-form>

      <div class="action-row">
        <el-button type="success" @click="saveSettings">{{ t('common.save') }}</el-button>
      </div>
    </div>

    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('settings.chromeTitle') }}</h3>
          <p class="panel-desc">{{ t('settings.chromeDesc') }}</p>
        </div>
        <el-tag :type="engineTag(store.engines.chrome)">{{ engineLabel(store.engines.chrome) }}</el-tag>
      </div>
    </div>

    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('settings.firefoxTitle') }}</h3>
          <p class="panel-desc">{{ t('settings.firefoxDesc') }}</p>
        </div>
        <el-tag :type="engineTag(store.engines.firefox)">{{ engineLabel(store.engines.firefox) }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useProfileStore } from '../stores/profile.js'

const { t } = useI18n()
const store = useProfileStore()
const form = ref(defaultSettings())

watch(
  () => store.settings,
  value => {
    if (value) {
      form.value = JSON.parse(JSON.stringify(value))
    }
  },
  { immediate: true, deep: true },
)

function defaultSettings() {
  return {
    language: 'zh-CN',
    theme_mode: 'system',
    user_data_root: '',
    chrome: {
      executable_path: '',
      installer_url: '',
      download_path: '',
      keep_installer: true,
    },
    firefox: {
      executable_path: '',
      installer_url: '',
      download_path: '',
      keep_installer: true,
    },
    api_access: {
      enabled: true,
      api_key: '',
      backend_only_port: 18000,
    },
    saved_proxies: [],
  }
}

function engineTag(engine) {
  if (!engine?.installed) return 'danger'
  if (engine?.capability_ok === false) return 'warning'
  return 'success'
}

function engineLabel(engine) {
  if (!engine?.installed) return t('engine.notInstalled')
  if (engine?.capability_ok === false) return t('engine.needFingerprintBuild')
  return t('engine.ready')
}

async function saveSettings() {
  try {
    await store.updateSettings(form.value)
    ElMessage.success(t('settings.saved'))
  } catch (error) {
    ElMessage.error(error.message)
  }
}
</script>
