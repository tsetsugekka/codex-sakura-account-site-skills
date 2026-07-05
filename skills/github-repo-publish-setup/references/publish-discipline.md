# Publish Discipline

Use this checklist before every publish:

1. `git branch --show-current`
2. `git status --short`
3. Review `git diff --stat`
4. Stage only intended files.
5. Commit with a concrete message.
6. Push the intended branch.

Do not:

- Create or switch branches unless requested.
- Keep using an old temporary branch by inertia when the user asked to publish.
- Revert user changes.
- Stage secrets or unrelated files.
- Commit generated caches unless the repository requires them.

If a deploy already happened before commit, mention that in the final response with the commit hash.

If unrelated changes are present, stop before staging and ask which files belong to the publish.
