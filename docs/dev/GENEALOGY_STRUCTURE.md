# Genealogy Data Structure

## Overview

The genealogy data has been reorganized from a single 3200+ line JSON file into multiple era-based files for improved maintainability and collaboration.

## File Structure

```
src/data/genealogy/
├── index.json                  (metadata, lineages, calendar info, era definitions)
├── antediluvian.json           (Adam-Noah, 13 people)
├── patriarchal.json            (Post-Flood patriarchs-Judah, 19 people)
├── conquest-judges.json        (Hezron-Solomon, 14 people)
├── divided-kingdom.json        (Rehoboam-Josiah, 15 people)
├── exile-return.json           (Jehoiakim-Zerubbabel, 4 people)
└── second-temple.json          (Abiud-Jesus, 12 people)
```

**Total: 77 people across 6 biblical eras**

## Benefits

- **Maintainability**: Each era is ~300-600 lines, much easier to edit than 3200 lines
- **Collaboration**: Different team members can work on different eras simultaneously without merge conflicts
- **Git Diffs**: Changes to specific eras are isolated, making code review easier
- **Logical Organization**: Eras mirror the natural biblical chronology
- **Scalability**: Easy to add new genealogies or extend existing eras

## Component Architecture

[GenealogyViewer.jsx](../../src/components/GenealogyViewer.jsx) automatically:
1. Imports all 6 era files plus the index
2. Merges all people arrays on component mount
3. Reconstructs the full genealogy structure
4. Provides all original filtering/viewing functionality

The merge is transparent to all downstream logic—parent-child relationships, lineage assignments, and queries work exactly as before.

## Data Integrity

All parent-child relationships are preserved across era boundaries:
- Example: Joseph (second-temple) → Jacob (second-temple), but Jacob's lineage traces back through multiple eras to Adam (antediluvian)
- All 77 people IDs remain consistent across files
- Lineage objects defined in index.json apply to people across all eras

## Era Definitions

### Antediluvian (13 people)
- **Date Range**: Zadok 0-1656 (Gregorian -4004 to -2348)
- **Description**: From creation of Adam to the Great Flood
- **Patriarchs**: Adam, Seth, Noah
- **File**: antediluvian.json

### Patriarchal (19 people)
- **Date Range**: Zadok 1656-2554 (Gregorian -2348 to -1450)
- **Description**: Post-Flood patriarchs through Egyptian sojourn and Conquest preparation
- **Patriarchs**: Abraham, Isaac, Jacob, Judah
- **File**: patriarchal.json

### Conquest & Judges (14 people)
- **Date Range**: Zadok 2554-3050 (Gregorian -1450 to -954)
- **Description**: From Conquest of Canaan through Judges era to monarchy establishment
- **Key Figures**: Samson, Boaz, Ruth, David, Solomon
- **File**: conquest-judges.json

### Divided Kingdom (15 people)
- **Date Range**: Zadok 3050-3400 (Gregorian -954 to -604)
- **Description**: From division of Solomon's kingdom through fall of Judah
- **Kings**: Rehoboam, Asa, Jehoshaphat, Josiah (15 total)
- **File**: divided-kingdom.json

### Exile & Return (4 people)
- **Date Range**: Zadok 3400-3520 (Gregorian -604 to -484)
- **Description**: Babylonian exile through return and temple rebuilding
- **Key Figures**: Zerubbabel, Shealtiel
- **File**: exile-return.json

### Second Temple (12 people)
- **Date Range**: Zadok 3520-4034 (Gregorian -484 to 30 AD)
- **Description**: Post-exile Jerusalem through Jesus Christ
- **Key Figures**: Joseph, Mary, Jesus
- **File**: second-temple.json

## Adding Data

To add a new person to the genealogy:

1. **Determine the era** based on their historical period
2. **Open the corresponding era file** (e.g., `divided-kingdom.json` for a Judean king)
3. **Add the person object** to the `people` array with:
   - `id`: Unique identifier (lowercase, underscores for multi-word)
   - `name`: Full name
   - `title`: Role/description
   - `zadok_year_born`, `gregorian_year_born`: Birth dates
   - `zadok_year_died`, `gregorian_year_died`: Death dates
   - `lifespan_years`: Calculated difference
   - `parent_id`: Reference to parent (must exist in any era file)
   - `spouse_id`: Reference to spouse (optional)
   - `children`: Array of child IDs
   - `lineages`: Array of lineage assignments from index.json
   - `data_classification`: "ACTUAL", "CALCULATED", "TRADITIONAL", or "EXTRAPOLATED"
   - `era`: Era name matching file
   - `major_events`: Array with event details and dates
   - `bible_references`: Array of scripture citations

4. **Update parent's `children` array** if adding as a child
5. **Update index.json** if creating new lineages or adding query definitions
6. **Validate**: Ensure parent IDs exist and all relationships are consistent

## Migration from Old Structure

The original `genealogy.json` has been superseded by the new modular structure. The file remains in the data directory for reference but is no longer used by the application.

To completely clean up:
```bash
rm src/data/genealogy.json
```

## Validation

Run the validation script to check data integrity:
```bash
python validate_genealogy.py
```

Expected output:
- All 6 era files load successfully
- Total of 77 people across all eras
- All parent-child links are valid (no orphaned references)
