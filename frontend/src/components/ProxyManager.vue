<template>
  <div class="proxy-manager-grid">
    <div class="proxy-manager-left">
      <div class="page-panel">
        <div class="panel-title-row">
          <div>
            <h3>{{ t('savedProxy.formTitle') }}</h3>
            <p class="panel-desc">{{ t('savedProxy.formDesc') }}</p>
          </div>
        </div>

        <el-form label-position="top" class="proxy-form">
          <el-form-item :label="t('savedProxy.name')">
            <el-input v-model="form.name" :placeholder="t('savedProxy.namePlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('proxy.type')">
            <el-segmented v-model="form.type" :options="proxyTypeOptions" />
          </el-form-item>

          <el-row :gutter="12">
            <el-col :span="16">
              <el-form-item :label="t('proxy.host')">
                <el-input v-model="form.host" :placeholder="t('proxy.hostPlaceholder')" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item :label="t('proxy.port')">
                <el-input v-model="form.port" type="number" :placeholder="t('proxy.portPlaceholder')" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item :label="t('proxy.username')">
                <el-input v-model="form.username" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="t('proxy.password')">
                <el-input v-model="form.password" type="password" show-password />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item :label="t('proxy.quickPaste')">
            <el-input v-model="quickProxyInput" :placeholder="t('proxy.quickPastePlaceholder')" @keyup.enter="parseQuickProxy">
              <template #append>
                <el-button @click="parseQuickProxy">{{ t('common.parse') }}</el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item :label="t('savedProxy.remark')">
            <el-input v-model="form.remark" type="textarea" :rows="2" :placeholder="t('savedProxy.remarkPlaceholder')" />
          </el-form-item>

          <div class="proxy-form-actions">
            <div class="action-row">
              <el-button type="primary" :disabled="!canSaveNew" @click="handleCreate">
                {{ t('common.add') }}
              </el-button>
              <el-button plain :loading="proxyChecking" :disabled="!canSaveNew" @click="handleTestNew">
                {{ t('proxy.testConnection') }}
              </el-button>
            </div>
            <transition name="fade">
              <el-tag v-if="proxyCheckResult" :type="proxyCheckResult.ok ? 'success' : 'danger'" class="proxy-check-tag">
                {{ proxyCheckResult.message }}
              </el-tag>
            </transition>
          </div>
        </el-form>
      </div>

      <div class="page-panel">
        <div class="panel-title-row">
          <div>
            <h3>{{ t('savedProxy.listTitle') }}</h3>
            <p class="panel-desc">{{ t('savedProxy.listDesc') }}</p>
          </div>
          <el-tag v-if="store.savedProxies.length" type="info" effect="plain">
            {{ store.savedProxies.length }}
          </el-tag>
        </div>

        <div v-if="store.savedProxies.length" class="saved-proxy-list">
          <div
            v-for="item in store.savedProxies"
            :key="item.id"
            class="saved-proxy-card"
            :class="{ active: selectedProxyId === item.id }"
            @click="selectedProxyId = item.id"
          >
            <div class="saved-proxy-card__header">
              <div class="saved-proxy-card__info">
                <div class="saved-proxy-card__title">{{ item.name }}</div>
                <div class="saved-proxy-card__meta">
                  <el-tag size="small" :type="item.type === 'socks5' ? 'warning' : 'success'" effect="plain">
                    {{ item.type.toUpperCase() }}
                  </el-tag>
                  <span class="muted-text">{{ item.host }}:{{ item.port }}</span>
                </div>
              </div>
              <div class="saved-proxy-card__actions">
                <el-button size="small" plain @click.stop="openEditDialog(item)">{{ t('common.edit') }}</el-button>
                <el-button size="small" type="danger" plain @click.stop="handleDelete(item)">{{ t('common.delete') }}</el-button>
              </div>
            </div>
            <div v-if="item.remark" class="muted-text" style="margin-top: 6px">{{ item.remark }}</div>
          </div>
        </div>
        <div v-else class="empty-state">
          <el-icon><Connection /></el-icon>
          <h3>{{ t('savedProxy.emptyTitle') }}</h3>
          <p>{{ t('savedProxy.emptyDesc') }}</p>
        </div>
      </div>
    </div>

    <div class="page-panel proxy-assign-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('savedProxy.assignTitle') }}</h3>
          <p class="panel-desc">{{ t('savedProxy.assignDesc') }}</p>
        </div>
      </div>

      <div class="proxy-assign-current">
        <div class="proxy-assign-label">{{ t('savedProxy.currentProxy') }}</div>
        <div class="proxy-assign-value" :class="{ active: selectedProxy }">
          <template v-if="selectedProxy">
            <el-tag size="small" :type="selectedProxy.type === 'socks5' ? 'warning' : 'success'" effect="plain">
              {{ selectedProxy.type.toUpperCase() }}
            </el-tag>
            <span>{{ selectedProxy.name }} &middot; {{ selectedProxy.host }}:{{ selectedProxy.port }}</span>
          </template>
          <span v-else class="muted-text">{{ t('savedProxy.notSelected') }}</span>
        </div>
      </div>

      <div class="profile-toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="profileSearch"
            :placeholder="t('savedProxy.profileSearchPlaceholder')"
            clearable
            :prefix-icon="Search"
            style="width: 240px"
          />
        </div>
        <div class="toolbar-right">
          <el-button type="primary" :disabled="!selectedProxy || !selectedProfileIds.length" @click="assignToProfiles">
            {{ t('savedProxy.assignButton', { n: selectedProfileIds.length }) }}
          </el-button>
        </div>
      </div>

      <el-table
        v-if="filteredProfiles.length"
        :data="filteredProfiles"
        row-key="id"
        @selection-change="rows => { selectedProfileIds = rows.map(item => item.id) }"
      >
        <el-table-column type="selection" width="44" />
        <el-table-column :label="t('profile.columns.profile')" min-width="200">
          <template #default="{ row }">
            <div class="profile-name">{{ row.name || t('common.unnamed') }}</div>
            <div class="muted-text">{{ row.group || '—' }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="t('profile.columns.engine')" width="110">
          <template #default="{ row }">
            <el-tag :type="row.engine === 'chrome' ? 'primary' : 'warning'" effect="plain" size="small">
              {{ row.engine === 'chrome' ? 'Chrome' : 'Firefox' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('profile.columns.proxy')" min-width="200">
          <template #default="{ row }">
            <span v-if="row.proxy.type !== 'none' && row.proxy.host" class="proxy-line">
              <el-tag size="small" :type="row.proxy.type === 'socks5' ? 'warning' : 'success'" effect="plain">
                {{ row.proxy.type.toUpperCase() }}
              </el-tag>
              <span>{{ row.proxy.host }}:{{ row.proxy.port }}</span>
            </span>
            <span v-else class="muted-text">{{ t('common.direct') }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-else class="empty-state">
        <el-icon><Monitor /></el-icon>
        <h3>{{ t('savedProxy.noProfilesTitle') }}</h3>
        <p>{{ t('savedProxy.noProfilesDesc') }}</p>
      </div>
    </div>

    <!-- Edit Proxy Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
      class="proxy-edit-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <h3>{{ t('common.edit') }}</h3>
          <p>{{ editForm.name }}</p>
        </div>
      </template>

      <el-form label-position="top" class="proxy-form">
        <el-form-item :label="t('savedProxy.name')">
          <el-input v-model="editForm.name" :placeholder="t('savedProxy.namePlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('proxy.type')">
          <el-segmented v-model="editForm.type" :options="proxyTypeOptions" />
        </el-form-item>

        <el-row :gutter="12">
          <el-col :span="16">
            <el-form-item :label="t('proxy.host')">
              <el-input v-model="editForm.host" :placeholder="t('proxy.hostPlaceholder')" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('proxy.port')">
              <el-input v-model="editForm.port" type="number" :placeholder="t('proxy.portPlaceholder')" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('proxy.username')">
              <el-input v-model="editForm.username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('proxy.password')">
              <el-input v-model="editForm.password" type="password" show-password />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="t('savedProxy.remark')">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" :placeholder="t('savedProxy.remarkPlaceholder')" />
        </el-form-item>

        <div class="proxy-form-actions">
          <el-button plain :loading="editProxyChecking" :disabled="!canSaveEdit" @click="handleTestEdit">
            {{ t('proxy.testConnection') }}
          </el-button>
          <transition name="fade">
            <el-tag v-if="editProxyCheckResult" :type="editProxyCheckResult.ok ? 'success' : 'danger'" class="proxy-check-tag">
              {{ editProxyCheckResult.message }}
            </el-tag>
          </transition>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button plain @click="editDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :disabled="!canSaveEdit" :loading="editSaving" @click="handleEditSave">
            {{ t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Monitor, Search } from '@element-plus/icons-vue'
import { useProfileStore } from '../stores/profile.js'

const { t } = useI18n()
const store = useProfileStore()

const quickProxyInput = ref('')
const profileSearch = ref('')
const proxyChecking = ref(false)
const proxyCheckResult = ref(null)
const selectedProxyId = ref('')
const selectedProfileIds = ref([])
const form = ref(createEmptyProxy())

const editDialogVisible = ref(false)
const editForm = ref(createEmptyProxy())
const editProxyChecking = ref(false)
const editProxyCheckResult = ref(null)
const editSaving = ref(false)

const proxyTypeOptions = [
  { label: 'HTTP', value: 'http' },
  { label: 'HTTPS', value: 'https' },
  { label: 'SOCKS5', value: 'socks5' },
]

const selectedProxy = computed(() => (
  store.savedProxies.find(item => item.id === selectedProxyId.value) || null
))

const filteredProfiles = computed(() => {
  const query = profileSearch.value.trim().toLowerCase()
  if (!query) return store.profiles
  return store.profiles.filter(item =>
    [item.name, item.group, item.remark]
      .filter(Boolean)
      .some(text => String(text).toLowerCase().includes(query))
  )
})

const canSaveNew = computed(() => Boolean(form.value.host && form.value.port))
const canSaveEdit = computed(() => Boolean(editForm.value.host && editForm.value.port))

watch(
  () => store.savedProxies,
  proxies => {
    if (!proxies.length) {
      selectedProxyId.value = ''
      return
    }
    if (selectedProxyId.value && proxies.some(item => item.id === selectedProxyId.value)) return
    selectedProxyId.value = proxies[0].id
  },
  { immediate: true, deep: true },
)

function createEmptyProxy() {
  return {
    id: '',
    name: '',
    type: 'http',
    host: '',
    port: null,
    username: '',
    password: '',
    remark: '',
  }
}

function resetForm() {
  form.value = createEmptyProxy()
  quickProxyInput.value = ''
  proxyCheckResult.value = null
}

function openEditDialog(item) {
  editForm.value = JSON.parse(JSON.stringify(item))
  editProxyCheckResult.value = null
  editDialogVisible.value = true
}

function parseQuickProxy() {
  const input = quickProxyInput.value.trim()
  if (!input) return
  try {
    if (input.includes('://')) {
      const url = new URL(input)
      form.value.type = url.protocol.replace(':', '')
      form.value.host = url.hostname
      form.value.port = Number(url.port || 0) || null
      form.value.username = decodeURIComponent(url.username || '')
      form.value.password = decodeURIComponent(url.password || '')
    } else {
      const [host, port, username, password] = input.split(':')
      form.value.host = host || ''
      form.value.port = Number(port || 0) || null
      form.value.username = username || ''
      form.value.password = password || ''
    }
    quickProxyInput.value = ''
  } catch {
    ElMessage.warning(t('proxy.parseError'))
  }
}

async function handleTestNew() {
  proxyChecking.value = true
  proxyCheckResult.value = null
  try {
    proxyCheckResult.value = await store.testProxy(form.value)
  } catch (error) {
    proxyCheckResult.value = { ok: false, message: error.message }
  } finally {
    proxyChecking.value = false
  }
}

async function handleTestEdit() {
  editProxyChecking.value = true
  editProxyCheckResult.value = null
  try {
    editProxyCheckResult.value = await store.testProxy(editForm.value)
  } catch (error) {
    editProxyCheckResult.value = { ok: false, message: error.message }
  } finally {
    editProxyChecking.value = false
  }
}

async function handleCreate() {
  try {
    const payload = JSON.parse(JSON.stringify(form.value))
    delete payload.id
    payload.port = Number(payload.port || 0) || null
    await store.saveSavedProxy(payload)
    resetForm()
    ElMessage.success(t('savedProxy.created'))
  } catch (error) {
    ElMessage.error(error.message)
  }
}

async function handleEditSave() {
  editSaving.value = true
  try {
    const payload = JSON.parse(JSON.stringify(editForm.value))
    payload.port = Number(payload.port || 0) || null
    const saved = await store.saveSavedProxy(payload)
    selectedProxyId.value = saved.id
    editDialogVisible.value = false
    ElMessage.success(t('savedProxy.updated'))
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    editSaving.value = false
  }
}

async function handleDelete(item) {
  await ElMessageBox.confirm(
    t('savedProxy.confirmDelete', { name: item.name }),
    t('profile.confirmDeleteTitle'),
    {
      type: 'warning',
      confirmButtonText: t('common.delete'),
      cancelButtonText: t('common.cancel'),
    },
  )
  try {
    await store.deleteSavedProxy(item.id)
    if (selectedProxyId.value === item.id) {
      selectedProxyId.value = ''
    }
    ElMessage.success(t('savedProxy.deleted'))
  } catch (error) {
    ElMessage.error(error.message)
  }
}

async function assignToProfiles() {
  try {
    await store.assignSavedProxy(selectedProxyId.value, selectedProfileIds.value)
    ElMessage.success(t('savedProxy.assigned', { n: selectedProfileIds.value.length }))
    selectedProfileIds.value = []
  } catch (error) {
    ElMessage.error(error.message)
  }
}
</script>

<style scoped>
.proxy-form .el-form-item {
  margin-bottom: 14px;
}

.proxy-form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 4px;
}

.proxy-check-tag {
  animation: fadeIn 0.3s ease;
}

.proxy-assign-current {
  padding: 14px;
  border-radius: var(--oab-radius-md);
  background: var(--oab-card-bg);
  border: 1px solid var(--oab-border);
  margin-bottom: 16px;
}

.proxy-assign-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--oab-muted);
  margin-bottom: 8px;
}

.proxy-assign-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

.proxy-assign-value.active {
  color: var(--oab-accent);
}

.proxy-assign-panel {
  display: flex;
  flex-direction: column;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
