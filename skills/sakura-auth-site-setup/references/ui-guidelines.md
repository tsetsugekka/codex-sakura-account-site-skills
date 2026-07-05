# UI Guidelines

Admin/supervisor screens should feel like the existing site, not a generic control panel.

Use:

- existing sidebar and header where possible,
- compact cards for individual tools,
- 8px to 10px radius unless the site already uses another radius,
- restrained colors from the current site,
- clear labels in Japanese,
- predictable table and form layouts,
- input padding that matches the site's existing controls.

Avoid:

- landing-page hero sections,
- decorative gradients,
- nested cards,
- oversized headings inside compact panels,
- visible explanatory text about how the app works,
- changing public navigation unless requested.

Form spacing notes:

- If text touches the left border of an input, inspect inherited `padding`, `line-height`, `text-indent`, `box-sizing`, and component-specific selectors before increasing the whole card's padding.
- Prefer fixing the input's own horizontal padding over adding large surrounding whitespace.
- Test the exact rendered admin page after deploy; CSS that works in a local component can be overridden by shared sidebar/admin styles.

Validation:

1. Build the admin page.
2. Open the live or local page.
3. Check that text is not clipped or touching borders.
4. Check desktop and narrow viewport.
5. Confirm protected and public pages behave as documented.
