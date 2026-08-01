import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'QmClient',
  description: '栖梦 QmClient —— 基于 DDNet 的中文定制客户端，更新日志与教程',
  srcDir: 'docs',
  cleanUrls: true,
  lastUpdated: true,
  markdown: {
    image: { lazyLoading: true },
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '更新日志', link: '/changelog/' },
      { text: '使用教程', link: '/guide/usage' },
      { text: '功能介绍', link: '/guide/features' },
      { text: 'Q&A', link: '/guide/qa' },
      { text: 'GitHub', link: 'https://github.com/wxj881027/QmClient' },
    ],
    sidebar: {
      '/guide/': [
        { text: '使用教程', link: '/guide/usage' },
        { text: '功能介绍', link: '/guide/features' },
        { text: 'Q&A', link: '/guide/qa' },
      ],
      '/changelog/': [
        { text: '📋 更新日志', link: '/changelog/' },
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/wxj881027/QmClient' },
    ],
    outline: { label: '本页目录', level: [2, 3] },
    docFooter: { prev: '上一篇', next: '下一篇' },
    lastUpdated: { text: '最后更新于', formatOptions: { dateStyle: 'full', timeStyle: 'medium' } },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '回到顶部',
    langMenuLabel: '语言',
  },
})
