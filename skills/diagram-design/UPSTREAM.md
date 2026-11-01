# Upstream source

- Project: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)
- Pinned tree: [`0cf73c3fcc56667ad91a9a04c439ac6ccfabc9d1`](https://github.com/cathrynlavery/diagram-design/tree/0cf73c3fcc56667ad91a9a04c439ac6ccfabc9d1)
- Upstream plugin version: 2.6.136
- License: MIT, copyright 2025 Cathryn Lavery; see [LICENSE](LICENSE).
- Bundled icon and font notices: see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

The 290 files in the upstream `skills/diagram-design/` directory are vendored unchanged at that commit. The upstream root `LICENSE` and `THIRD_PARTY_LICENSES.md` are also copied unchanged. No moving branch, runtime download, upstream installer, API key, or package dependency is required to discover and load the skill.

`README.md`, `SEVEN.md`, this file, `scripts/validate-diagram-design.mjs`, and the focused GitHub Actions workflow are local packaging additions. The upstream package's optional PNG helper requires an already installed Playwright runtime; it is not needed for native discovery or the smoke test.
