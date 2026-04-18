<template>
  <el-dialog
    :model-value="visible"
    width="960px"
    top="3vh"
    class="profile-dialog"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
  >
    <template #header>
      <div class="dialog-header">
        <div>
          <h3>{{ mode === 'create' ? t('dialog.createTitle') : t('dialog.editTitle') }}</h3>
          <p>{{ t('dialog.subtitle') }}</p>
        </div>
      </div>
    </template>

    <el-tabs v-model="activeTab" class="profile-tabs">
      <el-tab-pane :label="t('dialog.tabs.basic')" name="basic">
        <div class="dialog-grid">
          <div class="page-panel soft">
            <div class="form-section-title">{{ t('basic.title') }}</div>
            <el-form label-position="top">
              <el-form-item :label="t('basic.engine')" required>
                <el-segmented
                  v-model="form.engine"
                  :options="engineOptions"
                />
              </el-form-item>
              <el-form-item :label="t('basic.name')">
                <el-input v-model="form.name" :placeholder="t('basic.namePlaceholder')" maxlength="60" show-word-limit />
                <div class="form-tip">{{ t('basic.nameTip') }}</div>
              </el-form-item>
              <el-form-item :label="t('basic.group')">
                <el-select
                  v-model="form.group"
                  filterable
                  allow-create
                  clearable
                  style="width: 100%"
                  :placeholder="t('basic.groupPlaceholder')"
                >
                  <el-option v-for="group in store.groups" :key="group" :label="group" :value="group" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('basic.remark')">
                <el-input v-model="form.remark" type="textarea" :rows="2" :placeholder="t('basic.remarkPlaceholder')" />
              </el-form-item>
              <el-form-item :label="t('basic.storageRoot')">
                <el-input v-model="form.storage.root_dir" :placeholder="settingsUserDataPlaceholder" />
                <div class="form-tip">{{ t('basic.storageRootTip') }}</div>
              </el-form-item>
            </el-form>
          </div>

          <div class="page-panel soft">
            <div class="form-section-title">{{ t('basic.summary') }}</div>
            <div class="summary-list">
              <div class="summary-item">
                <span>{{ t('basic.engine') }}</span>
                <strong>{{ engineName }}</strong>
              </div>
              <div class="summary-item">
                <span>{{ t('profile.columns.proxy') }}</span>
                <strong>{{ proxySummary }}</strong>
              </div>
              <div class="summary-item">
                <span>{{ t('basic.storageRoot') }}</span>
                <strong>{{ form.storage.root_dir || settingsUserDataPlaceholder }}</strong>
              </div>
              <div class="summary-item">
                <span>{{ t('advanced.engineSource') }}</span>
                <strong>{{ t('advanced.bundledEngineText') }}</strong>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('dialog.tabs.proxy')" name="proxy">
        <div class="page-panel soft">
          <div class="form-section-title">{{ t('proxy.title') }}</div>
          <el-form label-position="top">
            <el-form-item :label="t('proxy.savedProxy')">
              <el-select
                v-model="selectedSavedProxyId"
                clearable
                filterable
                :teleported="false"
                style="width: 100%"
                :placeholder="t('proxy.savedProxyPlaceholder')"
                @change="applySavedProxy"
              >
                <el-option
                  v-for="item in store.savedProxies"
                  :key="item.id"
                  :label="`${item.name} · ${item.host}:${item.port}`"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('proxy.type')">
              <el-segmented v-model="form.proxy.type" :options="proxyTypeOptions" />
            </el-form-item>

            <template v-if="form.proxy.type !== 'none'">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-form-item :label="t('proxy.host')">
                    <el-input v-model="form.proxy.host" :placeholder="t('proxy.hostPlaceholder')" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item :label="t('proxy.port')">
                    <el-input v-model="form.proxy.port" type="number" :placeholder="t('proxy.portPlaceholder')" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="12">
                <el-col :span="12">
                  <el-form-item :label="t('proxy.username')">
                    <el-input v-model="form.proxy.username" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="t('proxy.password')">
                    <el-input v-model="form.proxy.password" show-password type="password" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item :label="t('proxy.quickPaste')">
                <el-input v-model="quickProxyInput" :placeholder="t('proxy.quickPastePlaceholder')" @keyup.enter="parseQuickProxy">
                  <template #append>
                    <el-button @click="parseQuickProxy">{{ t('common.parse') }}</el-button>
                  </template>
                </el-input>
                <div class="form-tip">{{ t('proxy.quickPasteTip') }}</div>
              </el-form-item>
              <div class="action-row">
                <el-button type="primary" plain :loading="proxyChecking" @click="checkProxy">
                  {{ t('proxy.testConnection') }}
                </el-button>
                <el-tag v-if="proxyCheckResult" :type="proxyCheckResult.ok ? 'success' : 'danger'">
                  {{ proxyCheckResult.message }}
                </el-tag>
              </div>
            </template>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('dialog.tabs.fingerprint')" name="fingerprint">
        <div v-if="form.engine === 'chrome'" class="page-panel soft">
          <div class="form-section-title">Chrome</div>
          <el-form label-position="top">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item :label="t('fingerprint.seed')">
                  <div class="inline-row">
                    <el-input v-model="chromeSeedText" type="number" :placeholder="t('fingerprint.seedPlaceholder')" />
                    <el-button @click="randomSeed">{{ t('common.random') }}</el-button>
                    <el-button plain @click="clearSeed">{{ t('common.clear') }}</el-button>
                  </div>
                  <div class="form-tip">{{ t('fingerprint.seedTip') }}</div>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.platform')">
                  <el-select v-model="form.chrome.fingerprint.platform">
                    <el-option label="Windows" value="windows" />
                    <el-option label="macOS" value="macos" />
                    <el-option label="Linux" value="linux" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.hardwareMode')">
                  <el-select v-model="form.chrome.fingerprint.hardware_concurrency_mode">
                    <el-option :label="t('common.auto')" value="auto" />
                    <el-option :label="t('common.manual')" value="manual" />
                    <el-option :label="t('common.random')" value="random" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="8" v-if="form.chrome.fingerprint.hardware_concurrency_mode === 'manual'">
                <el-form-item :label="t('fingerprint.cpuCores')">
                  <el-input v-model="form.chrome.fingerprint.hardware_concurrency" type="number" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.autoTimezone')">
                  <el-switch v-model="form.chrome.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.language')">
                  <el-input v-model="form.chrome.fingerprint.language" :disabled="form.chrome.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item :label="t('fingerprint.acceptLang')">
                  <el-input v-model="form.chrome.fingerprint.accept_language" :disabled="form.chrome.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="t('fingerprint.timezone')">
                  <el-input v-model="form.chrome.fingerprint.timezone" :disabled="form.chrome.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item :label="t('fingerprint.spoofingModules')">
              <el-checkbox-group v-model="form.chrome.fingerprint.disable_spoofing">
                <el-checkbox value="font" label="Font" />
                <el-checkbox value="audio" label="Audio" />
                <el-checkbox value="canvas" label="Canvas" />
                <el-checkbox value="clientrects" label="ClientRects" />
                <el-checkbox value="gpu" label="GPU" />
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </div>

        <div v-else class="page-panel soft">
          <div class="form-section-title">Firefox</div>
          <el-form label-position="top">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.autoTimezone')">
                  <el-switch v-model="form.firefox.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.language')">
                  <el-input v-model="form.firefox.fingerprint.language" :disabled="form.firefox.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.timezone')">
                  <el-input v-model="form.firefox.fingerprint.timezone" :disabled="form.firefox.fingerprint.auto_timezone" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.fontSystem')">
                  <el-select v-model="form.firefox.fingerprint.font_system">
                    <el-option label="windows" value="windows" />
                    <el-option label="mac" value="mac" />
                    <el-option label="linux" value="linux" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.screenMode')">
                  <el-select v-model="form.firefox.fingerprint.screen.mode">
                    <el-option :label="t('common.auto')" value="auto" />
                    <el-option :label="t('common.manual')" value="manual" />
                    <el-option :label="t('common.random')" value="random" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="form.firefox.fingerprint.screen.mode === 'manual'">
                <el-form-item :label="t('fingerprint.screenSize')">
                  <div class="inline-row">
                    <el-input v-model="form.firefox.fingerprint.screen.width" type="number" placeholder="W" />
                    <el-input v-model="form.firefox.fingerprint.screen.height" type="number" placeholder="H" />
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.hardwareMode')">
                  <el-select v-model="form.firefox.fingerprint.hardware_concurrency_mode">
                    <el-option :label="t('common.auto')" value="auto" />
                    <el-option :label="t('common.manual')" value="manual" />
                    <el-option :label="t('common.random')" value="random" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="form.firefox.fingerprint.hardware_concurrency_mode === 'manual'">
                <el-form-item :label="t('fingerprint.cpuCores')">
                  <el-input v-model="form.firefox.fingerprint.hardware_concurrency" type="number" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.webrtcMode')">
                  <el-select v-model="form.firefox.fingerprint.webrtc.mode">
                    <el-option :label="t('common.auto')" value="auto" />
                    <el-option :label="t('common.manual')" value="manual" />
                    <el-option :label="t('common.random')" value="random" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12" v-if="form.firefox.fingerprint.webrtc.mode === 'manual'">
              <el-col :span="12">
                <el-form-item :label="t('fingerprint.localIp')">
                  <el-input v-model="form.firefox.fingerprint.webrtc.local_ip" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="t('fingerprint.publicIp')">
                  <el-input v-model="form.firefox.fingerprint.webrtc.public_ip" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item :label="t('fingerprint.webglMode')">
                  <el-select v-model="form.firefox.fingerprint.webgl.mode">
                    <el-option :label="t('common.auto')" value="auto" />
                    <el-option :label="t('common.manual')" value="manual" />
                    <el-option :label="t('common.random')" value="random" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="16">
                <el-form-item :label="t('fingerprint.loadWebrtcBlock')">
                  <el-switch v-model="form.firefox.fingerprint.load_webrtc_block_extension" />
                </el-form-item>
              </el-col>
            </el-row>

            <template v-if="form.firefox.fingerprint.webgl.mode === 'manual'">
              <el-row :gutter="12">
                <el-col :span="12">
                  <el-form-item :label="t('fingerprint.webglVendor')">
                    <el-input v-model="form.firefox.fingerprint.webgl.vendor" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="t('fingerprint.webglRenderer')">
                    <el-input v-model="form.firefox.fingerprint.webgl.renderer" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="12">
                <el-col :span="12">
                  <el-form-item :label="t('fingerprint.webglVersion')">
                    <el-input v-model="form.firefox.fingerprint.webgl.version" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="t('fingerprint.webglGlsl')">
                    <el-input v-model="form.firefox.fingerprint.webgl.glsl_version" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <div class="sub-section-title">{{ t('fingerprint.extraFields') }}</div>
            <div v-for="(item, index) in form.firefox.fingerprint.extra_fields" :key="index" class="dynamic-row">
              <el-input v-model="item.key" :placeholder="t('fingerprint.extraKey')" />
              <el-input v-model="item.value" :placeholder="t('fingerprint.extraValue')" />
              <el-button type="danger" plain size="small" @click="removeExtraField(index)">{{ t('common.remove') }}</el-button>
            </div>
            <el-button plain @click="addExtraField">{{ t('fingerprint.addExtraField') }}</el-button>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('dialog.tabs.advanced')" name="advanced">
        <div class="page-panel soft">
          <div class="form-section-title">{{ t('advanced.title') }}</div>
          <el-form label-position="top">
            <el-form-item :label="t('advanced.windowSize')">
              <el-input v-model="engineConfig.startup.window_size" :placeholder="t('advanced.windowSizePlaceholder')" />
            </el-form-item>

            <el-form-item :label="t('advanced.startUrls')">
              <div class="tag-list" v-if="engineConfig.startup.open_urls.length">
                <el-tag v-for="(item, index) in engineConfig.startup.open_urls" :key="`${item}-${index}`" closable @close="removeUrl(index)">
                  {{ item }}
                </el-tag>
              </div>
              <el-input v-model="newUrl" :placeholder="t('advanced.startUrlsPlaceholder')" @keyup.enter="addUrl">
                <template #append>
                  <el-button @click="addUrl">{{ t('common.add') }}</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item :label="t('advanced.args')">
              <div class="tag-list" v-if="engineConfig.launch_args.length">
                <el-tag v-for="(item, index) in engineConfig.launch_args" :key="`${item}-${index}`" closable @close="removeArg(index)">
                  {{ item }}
                </el-tag>
              </div>
              <el-input v-model="newArg" :placeholder="t('advanced.argsPlaceholder')" @keyup.enter="addArg">
                <template #append>
                  <el-button @click="addArg">{{ t('common.add') }}</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item :label="t('advanced.globalExtensions')">
              <div v-if="availableGlobalExtensions.length" class="profile-extension-list">
                <div v-for="item in availableGlobalExtensions" :key="item.id" class="profile-extension-row">
                  <div>
                    <div class="profile-extension-title">{{ item.name }}</div>
                    <div class="muted-text">
                      {{ item.enabled ? t('extension.enabled') : t('extension.disabled') }} · {{ item.file_name }}
                    </div>
                  </div>
                  <el-switch
                    :model-value="isGlobalExtensionDisabled(item.id)"
                    :active-text="t('advanced.disableForProfile')"
                    :inactive-text="t('advanced.useForProfile')"
                    @change="value => toggleProfileExtensionDisabled(item.id, value)"
                  />
                </div>
              </div>
              <div v-else class="form-tip">{{ t('advanced.noGlobalExtensions') }}</div>
              <div class="form-tip">{{ t('advanced.globalExtensionsTip') }}</div>
            </el-form-item>

            <template v-if="form.engine === 'firefox'">
              <el-form-item :label="t('advanced.fingerprintFile')">
                <el-input v-model="form.firefox.fingerprint_file_path" :placeholder="t('advanced.fingerprintFilePlaceholder')" />
              </el-form-item>
            </template>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button plain @click="$emit('update:visible', false)">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ mode === 'create' ? t('common.create') : t('common.save') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { createDefaultProfile, useProfileStore } from '../stores/profile.js'

const { t } = useI18n()
const props = defineProps({
  visible: Boolean,
  profile: Object,
  mode: {
    type: String,
    default: 'create',
  },
})
const emit = defineEmits(['update:visible', 'saved'])

const store = useProfileStore()
const activeTab = ref('basic')
const saving = ref(false)
const proxyChecking = ref(false)
const proxyCheckResult = ref(null)
const selectedSavedProxyId = ref('')
const quickProxyInput = ref('')
const newArg = ref('')
const newUrl = ref('')
const newExtension = ref('')
const form = ref(createDefaultProfile())
let applyingSavedProxy = false

const engineOptions = [
  { label: 'Chrome', value: 'chrome' },
  { label: 'Firefox', value: 'firefox' },
]

const proxyTypeOptions = [
  { label: t('proxy.noProxy'), value: 'none' },
  { label: 'HTTP', value: 'http' },
  { label: 'HTTPS', value: 'https' },
  { label: 'SOCKS5', value: 'socks5' },
]

watch(
  () => props.profile,
  value => {
    form.value = value
      ? JSON.parse(JSON.stringify(value))
      : createDefaultProfile(store.settings)
    activeTab.value = 'basic'
    selectedSavedProxyId.value = ''
    quickProxyInput.value = ''
    proxyCheckResult.value = null
  },
  { immediate: true, deep: true },
)

watch(
  () => [store.savedProxies, form.value.proxy.type, form.value.proxy.host, form.value.proxy.port, form.value.proxy.username, form.value.proxy.password],
  () => {
    if (applyingSavedProxy) return
    const matchedId = findMatchingSavedProxyId(form.value.proxy)
    if (matchedId !== selectedSavedProxyId.value) {
      selectedSavedProxyId.value = matchedId
    }
  },
  { immediate: true, deep: true },
)

watch(selectedSavedProxyId, proxyId => {
  if (!proxyId) return
  applySavedProxy(proxyId)
})

const engineConfig = computed(() => (
  form.value.engine === 'chrome' ? form.value.chrome : form.value.firefox
))

const engineName = computed(() => (form.value.engine === 'chrome' ? 'Chrome' : 'Firefox'))
const settingsUserDataPlaceholder = computed(() => store.settings?.user_data_root || '')
const availableGlobalExtensions = computed(() => (
  store.managedExtensions.filter(item => item.engine === form.value.engine)
))
const proxySummary = computed(() => (
  form.value.proxy.type !== 'none' && form.value.proxy.host
    ? `${form.value.proxy.type.toUpperCase()} ${form.value.proxy.host}:${form.value.proxy.port || ''}`
    : t('common.direct')
))

const chromeSeedText = computed({
  get() {
    return form.value.chrome.fingerprint.seed == null ? '' : String(form.value.chrome.fingerprint.seed)
  },
  set(value) {
    const num = Number.parseInt(value, 10)
    form.value.chrome.fingerprint.seed = Number.isNaN(num) ? null : num
  },
})

function randomSeed() {
  form.value.chrome.fingerprint.seed = Math.floor(Math.random() * 0xffffffff)
}

function clearSeed() {
  form.value.chrome.fingerprint.seed = null
}

function findMatchingSavedProxyId(proxy) {
  const match = store.savedProxies.find(item =>
    item.type === proxy?.type &&
    item.host === proxy?.host &&
    Number(item.port || 0) === Number(proxy?.port || 0) &&
    (item.username || '') === (proxy?.username || '') &&
    (item.password || '') === (proxy?.password || '')
  )
  return match?.id || ''
}

function applySavedProxy(proxyId) {
  const selected = store.savedProxies.find(item => item.id === proxyId)
  if (!selected) return
  applyingSavedProxy = true
  form.value.proxy = {
    type: selected.type,
    host: selected.host,
    port: selected.port,
    username: selected.username,
    password: selected.password,
  }
  proxyCheckResult.value = null
  Promise.resolve().then(() => {
    applyingSavedProxy = false
  })
}

function parseQuickProxy() {
  const input = quickProxyInput.value.trim()
  if (!input) return
  try {
    if (input.includes('://')) {
      const url = new URL(input)
      form.value.proxy.type = url.protocol.replace(':', '')
      form.value.proxy.host = url.hostname
      form.value.proxy.port = Number(url.port || 0) || null
      form.value.proxy.username = decodeURIComponent(url.username || '')
      form.value.proxy.password = decodeURIComponent(url.password || '')
    } else {
      const [host, port, username, password] = input.split(':')
      form.value.proxy.type = form.value.proxy.type === 'none' ? 'http' : form.value.proxy.type
      form.value.proxy.host = host || ''
      form.value.proxy.port = Number(port || 0) || null
      form.value.proxy.username = username || ''
      form.value.proxy.password = password || ''
    }
    quickProxyInput.value = ''
  } catch {
    ElMessage.warning(t('proxy.parseError'))
  }
}

async function checkProxy() {
  proxyChecking.value = true
  proxyCheckResult.value = null
  try {
    proxyCheckResult.value = await store.testProxy(form.value.proxy)
  } catch (error) {
    proxyCheckResult.value = {
      ok: false,
      message: error.message,
    }
  } finally {
    proxyChecking.value = false
  }
}

function addArg() {
  pushUnique(engineConfig.value.launch_args, newArg.value)
  newArg.value = ''
}

function removeArg(index) {
  engineConfig.value.launch_args.splice(index, 1)
}

function addUrl() {
  pushUnique(engineConfig.value.startup.open_urls, newUrl.value)
  newUrl.value = ''
}

function removeUrl(index) {
  engineConfig.value.startup.open_urls.splice(index, 1)
}

function isGlobalExtensionDisabled(extensionId) {
  return engineConfig.value.disabled_global_extension_ids?.includes(extensionId) || false
}

function toggleProfileExtensionDisabled(extensionId, disabled) {
  const current = new Set(engineConfig.value.disabled_global_extension_ids || [])
  if (disabled) {
    current.add(extensionId)
  } else {
    current.delete(extensionId)
  }
  engineConfig.value.disabled_global_extension_ids = Array.from(current)
}

function addExtraField() {
  form.value.firefox.fingerprint.extra_fields.push({ key: '', value: '' })
}

function removeExtraField(index) {
  form.value.firefox.fingerprint.extra_fields.splice(index, 1)
}

function pushUnique(list, rawValue) {
  const value = String(rawValue || '').trim()
  if (!value) return
  if (!list.includes(value)) {
    list.push(value)
  }
}

async function handleSave() {
  saving.value = true
  try {
    const payload = JSON.parse(JSON.stringify(form.value))
    if (payload.proxy.port) payload.proxy.port = Number(payload.proxy.port)
    await store.saveProfile(payload)
    ElMessage.success(props.mode === 'create' ? t('dialog.savedCreated') : t('dialog.savedUpdated'))
    emit('saved')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
