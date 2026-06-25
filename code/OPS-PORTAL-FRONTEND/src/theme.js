// 主题切换
const THEME_KEY = 'ops-portal-theme'

export function getSavedTheme() {
  return localStorage.getItem(THEME_KEY) || 'light'
}

export function applyTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
  localStorage.setItem(THEME_KEY, theme)
}

export function toggleTheme() {
  const current = getSavedTheme()
  const next = current === 'light' ? 'dark' : 'light'
  applyTheme(next)
  return next
}

// 初始化
applyTheme(getSavedTheme())
