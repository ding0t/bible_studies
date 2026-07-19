# Gantt Timeline Enhancement - Feature Documentation

## Overview

The genealogy Gantt timeline has been enhanced with interactive features for better exploration and navigation:

1. **Clickable Names**: Person names are now hyperlinked to their detail view
2. **Year Scale Overlay**: Year markers are displayed directly on the timeline for reference
3. **Zoom Controls**: Range slider and buttons for adjusting timeline scale from 50% to 200%

## Features

### 1. Hyperlinked Names

**Description**: Every person's name in the Gantt timeline is now clickable

**Behavior**:
- Names appear in blue with underline, indicating they are clickable
- Clicking a name:
  1. Selects that person
  2. Automatically switches to the Details tab
  3. Shows comprehensive information about that person

**Visual Feedback**:
- Names have `cursor: pointer` to indicate interactivity
- Tooltip appears on hover: "Click to view [Name]'s details"
- Selected person's bar gets a dark border highlight

**Usage Example**:
```
Timeline view shows: Abraham (clickable)
User clicks → Details tab opens with Abraham's full genealogy
```

### 2. Hyperlinked Lifespan Bars

**Description**: Lifespan bars are also clickable for navigation

**Behavior**:
- Each colored bar represents a lifespan
- Clicking on any bar:
  1. Selects that person
  2. Switches to Details tab
  3. Highlights the bar with a dark border

**Visual Feedback**:
- Bars have `cursor: pointer` on hover
- Tooltip shows: "[Name]: [Start Year] to [End Year] ([Lifespan] years)"
- Opacity increases on hover for better visibility
- Selected person's bar shows dark border and full opacity

**Usage Example**:
```
Timeline shows red bars (Jesus's lineage) and blue bars (other patriarchs)
User hovers over David's bar → tooltip appears
User clicks David's bar → Details tab opens with David's information
```

### 3. Year Scale Overlay

**Description**: Year markers are displayed at the top of the timeline

**Features**:
- Year scale header shows at intervals of 200 years
- Tick marks align with the timeline bars below
- Year labels are positioned above the marks
- Scale is responsive and adjusts with zoom level

**Visual Design**:
- Tick marks: 2px wide vertical lines in gray (#6b7280)
- Year labels: Bold, small font (0.7em) in gray
- Header area: Bordered bottom (2px solid) to separate from bars
- Height: 32px to accommodate year labels

**Year Range**: 
- **Minimum Year**: -4100 (Zadok 0 = before the Flood)
- **Maximum Year**: -1800 (mid-Patriarchal era)
- **Interval**: 200 years between major marks

**Scale Calculation**:
```
Number of marks = ⌈(MaxYear - MinYear) / (200 / ZoomLevel)) + 1⌉
Mark position = ((year - MinYear) / (MaxYear - MinYear)) × 100%
```

**Example with 100% Zoom**:
```
-4100 | ... -3900 | ... -3700 | ... -3500 | ... etc.
```

**Example with 150% Zoom** (closer):
```
-4100 |     |  ... more marks visible ... | -3900
```

### 4. Zoom Controls

**Description**: Adjustable timeline zoom with range from 50% to 200%

**Controls**:

#### Zoom Out Button (−)
- **Function**: Decreases zoom level by 10%
- **Range**: 50% to 200%
- **Style**: Blue button with minus symbol
- **Behavior**: Disabled at 50% (minimum zoom)

#### Zoom Range Slider
- **Type**: HTML range input
- **Min**: 0.5 (50%)
- **Max**: 2.0 (200%)
- **Step**: 0.1 (10% increments)
- **Visual**: Standard range slider with blue track
- **Drag**: Smooth real-time zoom as you drag

#### Zoom In Button (+)
- **Function**: Increases zoom level by 10%
- **Range**: 50% to 200%
- **Style**: Blue button with plus symbol
- **Behavior**: Disabled at 200% (maximum zoom)

#### Zoom Percentage Display
- **Shows**: Current zoom level as percentage (e.g., "100%", "150%")
- **Updates**: Real-time as you adjust slider or click buttons
- **Font**: Bold, 0.9em, dark gray

**Control Panel Styling**:
- **Background**: Light blue (#f0f9ff)
- **Border**: 1px solid light blue border (#bfdbfe)
- **Padding**: 12px
- **Layout**: Flexbox with 12px gap
- **Border Radius**: 8px rounded corners
- **Position**: Above the timeline area

### 5. Zoom Effects

**50% Zoom** (Zoomed Out):
- Timeline compresses horizontally
- Shows more patriarchs on screen at once
- Year scale intervals compress (visible every 400+ years)
- Ideal for overview of entire genealogy

**100% Zoom** (Default):
- Balanced view showing ~15-20 patriarchs per screen
- Year scale shows 200-year intervals
- Bars clearly visible with lifespan labels

**150% Zoom** (Zoomed In):
- Timeline expands significantly
- Shows fewer patriarchs (5-10 per screen)
- Year scale becomes more granular
- Requires horizontal scrolling

**200% Zoom** (Maximum):
- Maximum horizontal expansion
- Very detailed view of individual lifespans
- Significant scrolling required
- Fine-grained year markers visible

**Dynamic Year Calculation**:
```
Year interval = 200 / zoomLevel
So at 50% zoom: 400-year intervals
At 100% zoom: 200-year intervals
At 200% zoom: 100-year intervals
```

## Technical Implementation

### State Management
```javascript
const [ganttZoom, setGanttZoom] = useState(1); // 1 = 100%
```

### Dynamic Width Calculation
```javascript
minWidth: `${800 * ganttZoom}px`  // Base 800px × zoom factor
```

### Name Click Handler
```javascript
onClick={() => {
  setSelectedPersonId(person.id);
  setActiveTab('details');
}}
```

### Bar Click Handler (same as name)
```javascript
onClick={() => {
  setSelectedPersonId(person.id);
  setActiveTab('details');
}}
```

### Year Scale Generation
```javascript
// Dynamic tick mark calculation
Array.from({ length: Math.ceil(((-1800 - (-4100)) / 200) * ganttZoom) + 1 })
  .map((_, i) => {
    const year = -4100 + (i * 200 / ganttZoom);
    const percentPos = ((year - (-4100)) / ((-1800) - (-4100))) * 100;
    // Render tick mark and label
  })
```

### Selected Person Highlighting
```javascript
border: selectedPersonId === person.id ? '2px solid #1f2937' : '1px solid rgba(0,0,0,0.1)',
opacity: selectedPersonId === person.id ? 1 : 0.8
```

## User Experience Improvements

### Navigation Flow
1. **Browse Timeline**: View all lifespans with Gantt bars
2. **Find Person**: Use zoom to locate person of interest
3. **Click Name or Bar**: Navigate to detailed view
4. **View Details**: See comprehensive information, events, relationships
5. **Return**: Navigate back to continue exploring

### Accessibility
- ✓ Color-coded bars (red = Jesus's lineage, blue = others)
- ✓ Tooltips on hover show full details
- ✓ Keyboard accessible range slider
- ✓ Large click targets (bars are 28px tall)
- ✓ Clear visual feedback for selections

### Performance Considerations
- ✓ Smooth zoom slider (no lag)
- ✓ Efficient year scale generation
- ✓ React optimized rendering (useMemo used elsewhere)
- ✓ No animation delays (instant zoom updates)

## Limitations & Notes

1. **Year Range**: Currently hardcoded to -4100 to -1800
   - Can be adjusted to show full -4100 to 30 AD range if desired
   - Would require adjusting minYear and maxYear constants

2. **Year Intervals**: Fixed at 200-year intervals
   - Could be made dynamic based on zoom level for better granularity
   - Current system shows fewer/more marks based on zoom

3. **Scroll Behavior**: Horizontal scroll required at zoom > 100%
   - Could add scroll-to-person feature
   - Could add autoscroll when selecting from other tabs

4. **Mobile Responsiveness**: Zoom controls work well on desktop
   - Touch-friendly on mobile but range slider may be finicky
   - Could add touch gesture support (pinch-zoom) in future

## Future Enhancement Ideas

### Planned
- [ ] Adjustable year range (show full -4100 to 30 AD)
- [ ] Dynamic year interval calculation based on zoom
- [ ] Timeline markers for biblical events
- [ ] Scroll-to-person when selected from other tabs
- [ ] Sticky header for year scale during scroll

### Nice-to-Have
- [ ] Pinch-zoom gesture support for touch devices
- [ ] Double-click to zoom to person
- [ ] Drag to pan when zoomed in
- [ ] Export timeline as image
- [ ] Keyboard shortcuts (+ and - keys for zoom)
- [ ] Custom zoom presets (Overview, Default, Detailed)

### Advanced
- [ ] Timeline filters (show only Jesus's lineage, specific era, etc.)
- [ ] Overlaid biblical events (major events, kingdoms, etc.)
- [ ] Connected relationships (show parent-child lines)
- [ ] Heat map of people alive in specific years
- [ ] Animation showing progression through time

## Testing Checklist

- [x] Build completes without errors
- [x] Component renders successfully
- [x] Zoom controls visible and styled correctly
- [x] Zoom slider moves smoothly from 50% to 200%
- [x] Zoom percentage display updates in real-time
- [x] Year scale renders and aligns with bars
- [x] Year scale adjusts with zoom level
- [x] Names are clickable and blue
- [x] Bars are clickable
- [x] Clicking name/bar selects person and switches to Details tab
- [x] Selected person's bar highlights with border
- [x] Tooltips display on hover
- [x] Legend shows Jesus's lineage (red) vs Others (blue)
- [ ] Full genealogy range (-4100 to 30 AD) works without errors
- [ ] All 77 people visible and clickable
- [ ] No performance degradation at max zoom

## Code Comments

The enhanced Gantt timeline includes inline comments explaining:
- Zoom controls UI and logic
- Year scale generation algorithm
- Click handlers for navigation
- Visual feedback styling
- Responsive width calculation

See [GenealogyViewer.jsx](../../src/components/GenealogyViewer.jsx) lines 368-525 for full implementation.
