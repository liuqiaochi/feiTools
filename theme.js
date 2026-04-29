/**
 * 老肥工具箱 - 主题切换
 * 在页面中引入此脚本，自动添加切换按钮并管理暗黑模式。
 */
(function() {
  // 读取保存的主题，默认跟随系统
  const saved = localStorage.getItem('fei-theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  // 创建切换按钮
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.createElement('button');
    btn.id = 'themeToggle';
    btn.setAttribute('aria-label', '切换暗黑模式');
    btn.innerHTML = isDark() ? '☀️' : '🌙';
    Object.assign(btn.style, {
      position: 'fixed', bottom: '20px', right: '20px', zIndex: '9999',
      width: '40px', height: '40px', borderRadius: '50%', border: 'none',
      fontSize: '18px', cursor: 'pointer', display: 'flex', alignItems: 'center',
      justifyContent: 'center', boxShadow: '0 2px 12px rgba(0,0,0,.15)',
      background: isDark() ? '#2a2a3e' : '#fff', transition: 'all .2s'
    });
    btn.addEventListener('click', function() {
      const dark = !isDark();
      document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
      localStorage.setItem('fei-theme', dark ? 'dark' : 'light');
      btn.innerHTML = dark ? '☀️' : '🌙';
      btn.style.background = dark ? '#2a2a3e' : '#fff';
      // 通知其他主题按钮同步更新
      window.dispatchEvent(new CustomEvent('fei-theme-changed', { detail: { dark } }));
    });
    document.body.appendChild(btn);
  });

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }
})();
