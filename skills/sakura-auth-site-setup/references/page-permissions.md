# Page Permissions

Separate these concepts:

- Protected page access.
- Navigation visibility.
- Public page placement.

Do not include a page in the role permission screen only because it appears in a staff-only navigation group. If a page is public, keep it out of role `pages` and document that it is public.

Recommended role model:

```json
[
  {"id": "user", "name": "User", "pages": [], "system": true},
  {"id": "staff", "name": "Staff", "pages": [], "system": true},
  {"id": "admin", "name": "管理者", "pages": ["*"], "system": true}
]
```

Admin role is fixed and cannot be downgraded through the UI.

Before changing page access:

1. List current public pages.
2. List current protected pages.
3. Confirm pages that should stay public.
4. Confirm pages that need role check.
5. Update docs with exact paths.

