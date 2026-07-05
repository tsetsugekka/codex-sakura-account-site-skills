# Page Permissions

Separate these concepts:

- Protected page access.
- Navigation visibility.
- Public page placement.

Do not include a page in the role permission screen only because it appears in a staff-only navigation group. If a page is public, keep it out of role `pages` and document that it is public.

Recommended role model:

```json
[
  {"id": "unverified", "name": "未認証", "pages": [], "system": true},
  {"id": "user", "name": "User", "pages": [], "system": true},
  {"id": "staff", "name": "Staff", "pages": [], "system": true},
  {"id": "admin", "name": "管理者", "pages": ["*"], "system": true}
]
```

Admin role is fixed and cannot be downgraded through the UI.

For pages with feature levels, define the permission keys on the page catalog, not as a global enum:

```php
'/example-tool/' => [
    'path' => '/example-tool/',
    'title' => 'Example Tool',
    'permissions' => [
        ['key' => 'read', 'label' => '閲覧のみ'],
        ['key' => 'operate', 'label' => '操作可能'],
        ['key' => 'manage', 'label' => '管理可能'],
    ],
],
```

The admin UI should offer `権限なし` plus the page-defined options for each role. Do not save page permissions directly on users.

Protected page entrypoints should inject a small runtime contract into the page. The global name must be project-scoped and configurable; examples include `window.SITE_AUTH`, `window.ACCOUNT_AUTH`, or another project-specific name.

```js
window.SITE_AUTH = {
  path: "/example-tool/",
  pagePermission: "operate",
  permissions: [
    { key: "read", label: "閲覧のみ" },
    { key: "operate", label: "操作可能" },
    { key: "manage", label: "管理可能" }
  ],
  user: { username: "example", roles: ["staff"] }
};
```

Page code must read `pagePermission`. It must not infer behavior from role names. If the page has its own API, the API must enforce the same permission server-side.

When handing work to another page-building thread, pass the permission contract document and the exact page permission keys. The page thread should not invent global permission levels.

Before changing page access:

1. List current public pages.
2. List current protected pages.
3. Confirm pages that should stay public.
4. Confirm pages that need role check.
5. Update docs with exact paths.
