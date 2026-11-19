# India Tourism Destination Directory Prototype

## Scope

`tourist_destinations_master.csv` contains 5,110 directory rows. This is a **visualization prototype**, not a verified registry of 5,110 real attractions. The visitor analytics use a separate 1,000-row sample in `5dvp.csv`.

## How to interpret the directory

- The catalogue combines a curated base list with entries generated from district-level templates.
- Template-generated names, ratings, costs, stay lengths, and point locations are illustrative. Point locations are approximate district-level placements, not surveyed attraction coordinates.
- Source URLs are portal references. They do not prove that each named attraction appears on that page or that each record was independently verified.
- The `Verification_Status` column now describes this limitation. A structurally valid URL or an in-bounds coordinate is not evidence that a place, rating, cost, or exact location is authentic.

## Appropriate use

Use the directory to demonstrate hierarchical GIS navigation and to discuss data quality. Use the separate visitor sample for visitor-record counts, ratings, trip-cost analysis, and recommendation calculations. Do not combine directory row counts with visitor-record counts or present prototype estimates as observed tourism statistics.

## Next step for a production-quality registry

Replace template-generated entries with individually sourced attraction records, store a direct page for each place, verify the place and coordinates, and record when each record was checked.
