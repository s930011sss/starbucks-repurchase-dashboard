# Dashboard Change Log

## 2026-06-21

### Starbucks-Inspired Redesign

- Redesigned the dashboard with a soft Starbucks-inspired product interface while preserving the existing member lookup, scoring, budget filter, and action-list data flow.
- Replaced the heavy dark visual system with tokenized primary green, secondary blue/cyan, neutral gray surfaces, rounded white cards, subtle borders, and soft shadows.
- Kept light mode as the default visual mode even on systems that prefer dark mode, while retaining dark-mode tokens for future switching.
- Restored the analytical layout into a left-side control rail and right-side dashboard output area with top metric cards, detail score rings, comparison bars, and a customer action table.
- Converted the customer action list from the default Streamlit dataframe to a styled HTML table for consistent premium card/table presentation.
- Updated Streamlit multiselect chips, number controls, and app chrome selectors so selected states and hidden controls follow the new green/neutral design system.
- Reduced the dashboard shell margin and padding so the left-side control rail fits cleanly in the 1440 x 960 desktop viewport.
- Tightened left-rail brand height, spacing, selected-filter chips, and budget summary tiles to preserve bottom spacing in the desktop canvas.
- Replaced the `Eligible filter` multiselect with a fixed checklist and selected-count badge so choosing more clusters no longer expands the left rail.
- Set the demo's default eligible cluster selection to four clusters to match the checklist presentation example.
- Removed the member lookup status badge, moved `Campaign Controls` upward, and increased the customer action table height so both sides fit more comfortably within the desktop canvas.
- Updated the default dashboard canvas background color to `#fbfaf5`.
- Added `prepare_dashboard_data.py` to merge `customer_segments.xlsx` and `Layer1_customer_uplift_scores.xlsx` into a dashboard-ready `dashboard_customers.csv`.
- Added Excel-to-dashboard feature mapping for cluster-based cost, value-based decision scoring, reward activity proxy, and population fit proxy.
- Updated the dashboard data loading logic to validate required CSV columns, derive eligible clusters from the active dataset, and fall back to the first available member when the old demo member ID is not present.
- Replaced the `Member vs Population Average` bar chart content with segment-specific narrative profile copy mapped by the active dataset's segment order, with fallback copy for unmapped segments.
- Made the segment narrative copy scroll within its card so longer profiles remain readable without changing the dashboard layout.
- Added default customer action list filters to exclude `Not clustered - no transactions` members and customers with negative uplift scores.
- Added a segment display-name mapping so `Low-Value Low-Response` remains the raw data value while the dashboard shows `Low-Spend Minimalists`.
- Replaced the `Source` summary tile with campaign ROI calculated as `(profit - cost) / cost`, where profit is the selected action list's summed `value * uplift_score`.
- Highlighted the Selected, Used Budget, Remaining, and ROI summary tiles with consistent KPI accent bars and subtle status-tinted backgrounds.
- Slightly enlarged the four campaign summary tiles and thickened their borders while preserving the two-column control layout.
- Added row-level ROI to the customer action list and reordered the table columns to `Customer ID`, `Cluster`, `Score`, `Cost`, and `ROI`.
- Left-aligned all customer action list column headers and added fixed column widths so the table fills the available space more evenly.
- Center-aligned the customer action list column headers while keeping row-level numeric values right-aligned.
- Realigned the customer action list with text columns left-aligned, numeric columns right-aligned, refined column widths, and currency formatting for Score values.
- Added right-side padding to the action list's ROI column so its header and values align more comfortably inside the table edge.
- Added an explicit eligible-cluster display order: High-Value Responsive, Dormant Value Customers, Frequent Light Buyers, Thin-History Low-Activity, and Low-Spend Minimalists.
- Updated campaign and row-level ROI to use cluster-based campaign values with CSV `value` as the fallback for unmapped clusters.
- Replaced the `Remaining` summary tile with campaign expected net profit calculated from the selected action list's summed `decision_score`.
- Realigned the `Net Profit` summary tile with ROI by calculating both from cluster-based campaign profit minus used budget.

### Earlier Layout Refinement

- Removed the left-side `Inspection Section` and `Action List Generator` label blocks.
- Expanded the main dashboard content to use the full page width.
- Realigned the top metrics, inspection cards, and action-list generator into three clean horizontal rows with consistent spacing.
- Tightened card heights, row spacing, widget padding, and table height so the desktop layout fits more cleanly in a 1440 x 960 viewport.
- Adjusted the top-row column ratio so the logo block aligns visually with the input and customize columns below.
- Preserved the previous dark blue SaaS visual style and CSV-backed demo data flow for that earlier iteration.
