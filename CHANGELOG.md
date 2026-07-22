# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-11

### Added
- **Astro Migration**: Migrated from mkdocs to Astro 4.16.19 static site generator
- **Interactive Timeline Component**: Built React-based timeline with zoom, pan, and event selection
- **Calendar View Toggle**: Added ability to switch between Gregorian and Zadok calendar views
- **Content Collections**: Implemented Astro Content Collections with TypeScript/Zod schema validation
- **New Frontmatter Fields**:
  - `bible_references`: Array of scripture references
  - `Zadok_year`: Event year in Zadok calendar (Year 0 = Adam's creation)
  - `Gregorian_year`: Event year in Gregorian calendar
- **Mermaid Diagram Support**: Integrated Mermaid.js for rendering diagrams in markdown (timelines, flowcharts, concept maps)
- **React Component Examples**: TimelineComponent and diagram integration patterns
- **Comprehensive Documentation**: Created CONTRIBUTING.md with field guide, templates, and diagram examples

### Changed
- **Frontmatter Normalization**: Updated all 109 markdown files with complete schema compliance
- **Bible Book Titles**: Preserved numeric prefixes (01 Genesis, 40 Matthew, etc.) for proper ordering
- **Timeline Component**: Enhanced to support dual calendar systems with fallback to year field

### Fixed
- **Content Layer API**: Enabled experimental contentLayer flag in astro.config.mjs
- **File Paths**: Corrected vite.ssr.external configuration for path module

### Technical Details
- Node.js: v24.12.0
- npm: 11.6.2
- Astro: 4.16.19
- React: 18.2.0
- Build Tool: Vite-based
- Dev Server: http://localhost:4321/

## [0.0.1] - Initial Release

### Initial Setup
- Project scaffolding and configuration
- Basic file structure
- Package dependencies

---

## Versioning Policy

This project follows **Semantic Versioning (SemVer)**:

- **MAJOR** (X.0.0): Breaking changes to content structure or API
- **MINOR** (0.X.0): New features, new frontmatter fields, UI enhancements
- **PATCH** (0.0.X): Bug fixes, documentation updates, minor improvements

### When to Bump Versions

- **Major**: Changes to frontmatter schema that require migration, breaking changes to timeline display
- **Minor**: New calendar types, new diagram support, new component features, new fields
- **Patch**: Content updates, typo fixes, small UI tweaks, dependency patches

### Release Process

1. Update version in `package.json`
2. Add entry to `CHANGELOG.md` with date and changes
3. Commit with message: `chore: bump version to X.Y.Z`
4. Create git tag: `git tag vX.Y.Z`
5. Push tag to GitHub for Release

Example:
```bash
npm version minor  # Auto-updates package.json
# Edit CHANGELOG.md
git add CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```
