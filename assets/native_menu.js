/* Streamlit 1.65 menu adapter. Only trusted static code; no CSV contents here.
 * Keep native appearance controls and menu behaviour, inserting two actions
 * before the first ordinary menu item. Native Python widgets handle transfers.
 * Recheck the browser smoke tests when upgrading Streamlit's frontend.
 */
(() => {
  window.prospectLensMenuObserver?.disconnect();
  const targets = {
    export: '.st-key-export_survey button',
    upload: '.st-key-menu_upload button'
  };
  function mount() {
    const menu = document.querySelector('[role="menu"][aria-label="Main menu"]');
    if (!menu) return;
    const first = menu.querySelector('[role="menuitem"]:not([data-pl-action])');
    if (!first) return;
    const exportTitle = document.querySelector(targets.export)?.textContent || 'Export CSV';
    for (const [action, title] of [['export', exportTitle], ['upload', 'Manage data']]) {
      let item = menu.querySelector(`[data-pl-action="${action}"]`);
      if (!item) {
        item = document.createElement('button');
        item.type = 'button';
        item.role = 'menuitem';
        item.tabIndex = -1;
        item.dataset.plAction = action;
        item.className = 'pl-menu-action';
        item.textContent = title;
        item.addEventListener('click', () => {
          const target = document.querySelector(targets[action]);
          if (!target || target.disabled) return;
          document.querySelector('button[aria-label="Main menu"]')?.click();
          target.click();
        });
        item.addEventListener('keydown', event => {
          if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
          const items = [...menu.querySelectorAll('[role^="menuitem"]')]
            .filter(el => el.getClientRects().length && !el.disabled);
          const index = items.indexOf(item);
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length-1 :
            (index + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
          event.preventDefault();
          event.stopPropagation();
          items[next]?.focus();
        });
        first.parentElement.insertBefore(item, first);
      }
      const target = document.querySelector(targets[action]);
      if (item.textContent !== title) item.textContent = title;
      item.disabled = !target || target.disabled;
    }
  }
  // Child-list observation catches menu openings and Streamlit rerenders.
  // Idempotent insertion avoids duplicates and attribute-observer loops.
  window.prospectLensMenuObserver = new MutationObserver(mount);
  window.prospectLensMenuObserver.observe(document.body, {childList: true, subtree: true});
  mount();
})();
