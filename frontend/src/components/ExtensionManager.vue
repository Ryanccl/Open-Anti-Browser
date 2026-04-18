<template>
  <div class="extensions-grid">
    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('extension.title') }}</h3>
          <p class="panel-desc">{{ t('extension.desc') }}</p>
        </div>
      </div>

      <el-form label-position="top">
        <el-form-item :label="t('extension.engine')">
          <el-segmented v-model="activeEngine" :options="engineOptions" />
        </el-form-item>

        <el-form-item :label="t('extension.name')">
          <el-input v-model="uploadName" :placeholder="t('extension.namePlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('extension.file')">
          <input
            ref="fileInputRef"
            class="hidden-file-input"
            type="file"
            :accept="acceptString"
            @change="handleFileChange"
          />
          <div class="extension-upload-box">
            <div>
              <div class="extension-upload-name">
                {{ selectedFile?.name || t('extension.noFile') }}
              </div>
              <div class="form-tip">
                {{ activeEngine === 'chrome' ? t('extension.chromeFormats') : t('extension.firefoxFormats') }}
              </div>
            </div>
            <div class="action-row">
              <el-button plain @click="triggerFileSelect">{{ t('extension.pickFile') }}</el-button>
              <el-button
                type="primary"
                :loading="uploading"
                :disabled="!selectedFile"
                @click="uploadFile"
              >
                {{ t('extension.upload') }}
              </el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item :label="t('extension.folder')">
          <div class="extension-upload-box">
            <div>
              <div class="extension-upload-name">
                {{ selectedFolder || t('extension.noFolder') }}
              </div>
              <div class="form-tip">
                {{ t('extension.folderTip') }}
              </div>
            </div>
            <div class="action-row">
              <el-button plain :loading="pickingFolder" @click="pickFolder">
                {{ t('extension.pickFolder') }}
              </el-button>
              <el-button
                type="primary"
                :loading="importingFolder"
                :disabled="!selectedFolder"
                @click="importFolder"
              >
                {{ t('extension.importFolder') }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-panel">
      <div class="panel-title-row">
        <div>
          <h3>{{ t('extension.listTitle') }}</h3>
          <p class="panel-desc">{{ t('extension.listDesc') }}</p>
        </div>
      </div>

      <div v-if="filteredExtensions.length" class="extension-card-list">
        <div v-for="item in filteredExtensions" :key="item.id" class="extension-card">
          <div class="extension-card__header">
            <div>
              <div class="extension-card__title">{{ item.name }}</div>
              <div class="muted-text">{{ item.file_name }}</div>
            </div>
            <el-tag :type="item.enabled ? 'success' : 'info'">
              {{ item.enabled ? t('extension.enabled') : t('extension.disabled') }}
            </el-tag>
          </div>

          <div class="summary-list extension-card__meta">
            <div class="summary-item">
              <span>{{ t('extension.scope') }}</span>
              <strong>{{ activeEngine === 'chrome' ? 'Chrome' : 'Firefox' }}</strong>
            </div>
            <div class="summary-item">
              <span>{{ t('extension.applyRule') }}</span>
              <strong>{{ t('extension.applyRuleDesc') }}</strong>
            </div>
          </div>

          <div class="action-row">
            <el-switch
              :model-value="item.enabled"
              :active-text="t('extension.enabled')"
              :inactive-text="t('extension.disabled')"
              @change="value => toggleExtension(item, value)"
            />
            <el-button type="danger" plain @click="deleteExtension(item)">
              {{ t('common.delete') }}
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><Files /></el-icon>
        <h3>{{ t('extension.emptyTitle') }}</h3>
        <p>{{ t('extension.emptyDesc') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Files } from '@element-plus/icons-vue'
import { useProfileStore } from '../stores/profile.js'

const { t } = useI18n()
const store = useProfileStore()

const activeEngine = ref('chrome')
const uploadName = ref('')
const selectedFile = ref(null)
const selectedFolder = ref('')
const uploading = ref(false)
const importingFolder = ref(false)
const pickingFolder = ref(false)
const fileInputRef = ref(null)

const engineOptions = [
  { label: 'Chrome', value: 'chrome' },
  { label: 'Firefox', value: 'firefox' },
]

const filteredExtensions = computed(() => (
  store.managedExtensions.filter(item => item.engine === activeEngine.value)
))

const acceptString = computed(() => (
  activeEngine.value === 'chrome' ? '.zip,.crx' : '.xpi,.zip'
))

watch(activeEngine, () => {
  selectedFile.value = null
  selectedFolder.value = ''
  uploadName.value = ''
  if (fileInputRef.value) fileInputRef.value.value = ''
})

function triggerFileSelect() {
  fileInputRef.value?.click()
}

function handleFileChange(event) {
  const files = event?.target?.files
  selectedFile.value = files && files.length ? files[0] : null
}

async function uploadFile() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    await store.uploadManagedExtension(activeEngine.value, selectedFile.value, uploadName.value)
    ElMessage.success(t('extension.uploaded'))
    uploadName.value = ''
    selectedFile.value = null
    if (fileInputRef.value) fileInputRef.value.value = ''
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    uploading.value = false
  }
}

async function pickFolder() {
  pickingFolder.value = true
  try {
    const result = await store.pickDirectory(t('extension.pickFolderTitle'), selectedFolder.value)
    selectedFolder.value = result?.path || ''
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    pickingFolder.value = false
  }
}

async function importFolder() {
  if (!selectedFolder.value) return
  importingFolder.value = true
  try {
    await store.importManagedExtensionFolder(activeEngine.value, selectedFolder.value, uploadName.value)
    ElMessage.success(t('extension.importedFolder'))
    uploadName.value = ''
    selectedFolder.value = ''
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    importingFolder.value = false
  }
}

async function toggleExtension(item, enabled) {
  try {
    await store.updateManagedExtension(item.id, { enabled })
    ElMessage.success(enabled ? t('extension.enabledMessage') : t('extension.disabledMessage'))
  } catch (error) {
    ElMessage.error(error.message)
  }
}

async function deleteExtension(item) {
  await ElMessageBox.confirm(
    t('extension.confirmDelete', { name: item.name }),
    t('profile.confirmDeleteTitle'),
    {
      type: 'warning',
      confirmButtonText: t('common.delete'),
      cancelButtonText: t('common.cancel'),
    },
  )
  try {
    await store.deleteManagedExtension(item.id)
    ElMessage.success(t('extension.deleted'))
  } catch (error) {
    ElMessage.error(error.message)
  }
}
</script>
