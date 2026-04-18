import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.js'
import enUS from './en-US.js'

const STORAGE_KEY = 'open-anti-browser.locale'
const SUPPORTED_LOCALES = ['zh-CN', 'en-US']

function normalizeLocale(locale) {
  return SUPPORTED_LOCALES.includes(locale) ? locale : 'zh-CN'
}

function readSavedLocale() {
  try {
    return normalizeLocale(window.localStorage.getItem(STORAGE_KEY) || '')
  } catch {
    return 'zh-CN'
  }
}

const i18n = createI18n({
  legacy: false,
  locale: readSavedLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
})

export function setLocale(locale) {
  const nextLocale = normalizeLocale(locale)
  i18n.global.locale.value = nextLocale
  document.documentElement.lang = nextLocale
  try {
    window.localStorage.setItem(STORAGE_KEY, nextLocale)
  } catch {
    // ignore
  }
}

export function getLocale() {
  return normalizeLocale(i18n.global.locale.value)
}

setLocale(readSavedLocale())

export default i18n
