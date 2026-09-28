const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const injector = path.resolve(__dirname, '../scripts/inject_deploy_refresh.py');
const marker = '<!-- DEPLOY_REFRESH_CHECK_V1 -->';
const currentHTML = '<html><head><script src="assets/main-old.js"></script><link rel="stylesheet" href="assets/site-old.css"></head></html>';
const latestHTML = '<html><head><script src="assets/main-new.js"></script><link rel="stylesheet" href="assets/site-new.css"></head></html>';

function injectedScript() {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'deploy-refresh-test-'));
  try {
    const target = path.join(temporary, 'index.html');
    fs.writeFileSync(target, currentHTML);
    execFileSync('python3', [injector, '--write', target]);
    const once = fs.readFileSync(target, 'utf8');
    assert.equal(once.split(marker).length - 1, 1);
    assert.doesNotMatch(once, /http-equiv=/i);
    execFileSync('python3', [injector, '--write', target]);
    assert.equal(fs.readFileSync(target, 'utf8'), once);
    const match = once.match(/<!-- DEPLOY_REFRESH_CHECK_V1 -->\s*<script>([\s\S]*?)<\/script>/);
    assert.ok(match);
    return match[1];
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

const script = injectedScript();

function parsedDocument(html) {
  const base = html.match(/<base\s+href=["']([^"']+)["']/i);
  const assets = [];
  for (const tag of html.matchAll(/<(script|link)\b([^>]*)>/gi)) {
    const attributes = Object.fromEntries(
      [...tag[2].matchAll(/([\w-]+)=["']([^"']*)["']/g)].map((part) => [part[1].toLowerCase(), part[2]]),
    );
    if ((tag[1].toLowerCase() === 'script' && attributes.src) ||
        (tag[1].toLowerCase() === 'link' && attributes.href && attributes.rel?.split(/\s+/).includes('stylesheet'))) {
      assets.push({ getAttribute: (name) => attributes[name] || null });
    }
  }
  return {
    querySelector: () => base ? { getAttribute: () => base[1] } : null,
    querySelectorAll: () => assets,
  };
}

function page(options = {}) {
  const loadedUrl = options.loadedUrl || 'https://example.test/section/?view=one';
  const location = {
    href: options.visibleUrl || loadedUrl,
    origin: new URL(loadedUrl).origin,
    replace(url) { reloads.push(url); },
  };
  const reloads = [];
  const fetched = [];
  const replaced = [];
  const timers = [];
  const listeners = new Map();
  const storage = options.storage || new Map();
  const document = {
    ...parsedDocument(options.currentHTML || currentHTML),
    title: 'Example',
    readyState: 'complete',
    visibilityState: options.visibilityState || 'visible',
    activeElement: options.activeElement || { tagName: 'BODY', isContentEditable: false },
    addEventListener(name, handler) { listeners.set(name, handler); },
  };
  const context = {
    URL,
    document,
    location,
    performance: { getEntriesByType: () => [{ name: loadedUrl }] },
    history: {
      state: null,
      replaceState(_state, _title, url) {
        replaced.push(url);
        location.href = url;
      },
    },
    sessionStorage: {
      getItem(key) {
        if (options.storageFails) throw new Error('storage unavailable');
        return storage.get(key) || null;
      },
      setItem(key, value) {
        if (options.storageFails) throw new Error('storage unavailable');
        storage.set(key, value);
      },
    },
    setTimeout(handler) { timers.push(handler); },
    fetch(url, request) {
      fetched.push({ url, request });
      if (options.fetchResponse) return options.fetchResponse(url);
      return Promise.resolve({
        ok: true,
        url: options.responseUrl || url,
        text: () => Promise.resolve(options.latestHTML || latestHTML),
      });
    },
    DOMParser: class {
      parseFromString(html) { return parsedDocument(html); }
    },
  };
  vm.runInNewContext(script, context);
  return {
    document, location, reloads, fetched, replaced, timers, storage,
    interact(name) { listeners.get(name)(); },
    async check() {
      assert.equal(timers.length, 1);
      timers.shift()();
      await new Promise(setImmediate);
    },
  };
}

test('injector is idempotent and does not add cache meta tags', () => {
  assert.match(script, /cache: 'no-cache'/);
  assert.doesNotMatch(script, /cache: 'no-store'|__deploy_check/);
});

test('revalidates the loaded route and cleans the reload parameter', async () => {
  const first = page();
  await first.check();
  assert.equal(first.fetched.length, 1);
  assert.equal(first.fetched[0].url, 'https://example.test/section/?view=one');
  assert.equal(first.fetched[0].request.cache, 'no-cache');
  assert.equal(first.fetched[0].request.credentials, 'same-origin');
  assert.equal(first.reloads.length, 1);
  const reloadUrl = new URL(first.reloads[0]);
  assert.equal(reloadUrl.pathname, '/section/');
  assert.equal(reloadUrl.searchParams.get('view'), 'one');
  assert.ok(reloadUrl.searchParams.get('__deploy_v'));

  const second = page({ loadedUrl: first.reloads[0], storage: first.storage });
  assert.equal(second.replaced.length, 1);
  assert.equal(new URL(second.replaced[0]).searchParams.has('__deploy_v'), false);
  await second.check();
  assert.equal(second.reloads.length, 0, 'the same target signature is attempted only once');
  assert.equal(second.fetched[0].url, 'https://example.test/section/?view=one');
});

test('skips a programmatic route or query change, including while the fetch is pending', async () => {
  const before = page();
  before.location.href = 'https://example.test/pushed/alias?view=two';
  await before.check();
  assert.equal(before.fetched.length, 0);
  assert.equal(before.reloads.length, 0);

  const changedQuery = page();
  changedQuery.location.href = 'https://example.test/section/?view=two';
  await changedQuery.check();
  assert.equal(changedQuery.fetched.length, 0);

  let resolveFetch;
  const during = page({ fetchResponse: () => new Promise((resolve) => { resolveFetch = resolve; }) });
  during.timers.shift()();
  assert.equal(during.fetched[0].url, 'https://example.test/section/?view=one');
  during.location.href = 'https://example.test/pushed/alias?view=two';
  resolveFetch({ ok: true, url: 'https://example.test/section/?view=one', text: () => Promise.resolve(latestHTML) });
  await new Promise(setImmediate);
  assert.equal(during.reloads.length, 0);
  assert.equal(during.storage.size, 0);

  const hashOnly = page();
  hashOnly.location.href += '#chart';
  await hashOnly.check();
  assert.equal(hashOnly.reloads.length, 1);
});

test('guards each target signature across A/B alternation and separates business queries', async () => {
  const storage = new Map();
  const first = page({ storage, currentHTML, latestHTML });
  await first.check();
  assert.equal(first.reloads.length, 1);

  const second = page({ storage, currentHTML: latestHTML, latestHTML: currentHTML });
  await second.check();
  assert.equal(second.reloads.length, 1);

  const third = page({ storage, currentHTML, latestHTML });
  await third.check();
  assert.equal(third.reloads.length, 0);
  assert.equal(storage.size, 2);

  const otherQuery = page({ storage, loadedUrl: 'https://example.test/section/?view=two' });
  await otherQuery.check();
  assert.equal(otherQuery.reloads.length, 1);
  assert.equal(storage.size, 3);
});

test('skips refresh after interaction before or during the check', async () => {
  const before = page();
  before.interact('input');
  await before.check();
  assert.equal(before.fetched.length, 0);

  let resolveFetch;
  const during = page({ fetchResponse: () => new Promise((resolve) => { resolveFetch = resolve; }) });
  during.timers.shift()();
  during.interact('pointerdown');
  resolveFetch({ ok: true, url: 'https://example.test/section/?view=one', text: () => Promise.resolve(latestHTML) });
  await new Promise(setImmediate);
  assert.equal(during.reloads.length, 0);
  assert.equal(during.storage.size, 0);
});

test('skips editing, hidden tabs, and unavailable storage', async () => {
  const cases = [
    { activeElement: { tagName: 'TEXTAREA', isContentEditable: false } },
    { activeElement: { tagName: 'DIV', isContentEditable: true } },
    { activeElement: { tagName: 'IFRAME', isContentEditable: false } },
    { visibilityState: 'hidden' },
    { storageFails: true },
  ];
  for (const options of cases) {
    const runtime = page(options);
    await runtime.check();
    assert.equal(runtime.reloads.length, 0);
  }
});

test('ignores cross-origin asset changes and redirected checks', async () => {
  const current = '<html><script src="/main-old.js"></script><script src="https://cdn.test/a.js"></script></html>';
  const latest = '<html><script src="/main-old.js"></script><script src="https://cdn.test/b.js"></script></html>';
  const externalOnly = page({ currentHTML: current, latestHTML: latest });
  await externalOnly.check();
  assert.equal(externalOnly.reloads.length, 0);

  const redirected = page({ responseUrl: 'https://example.test/login' });
  await redirected.check();
  assert.equal(redirected.reloads.length, 0);
});
