/**
 * Charts Rendering Module (Plotly.js Bridge)
 * Handles client-side rendering and responsive resizing of Plotly charts
 * received from Flask API backend.
 */

const Charts = {
    selectionHandler: null,

    setSelectionHandler: function(handler) {
        this.selectionHandler = handler;
    },

    selectionForPoint: function(chartId, point) {
        const x = point.x == null ? "" : String(point.x);
        const y = point.y == null ? "" : String(point.y);
        const label = point.label == null ? "" : String(point.label);
        const traceName = point.data && point.data.name ? String(point.data.name) : "";
        const custom = Array.isArray(point.customdata) ? point.customdata : [];
        const mappings = {
            "chart-state-volume": { state: y },
            "chart-segment-metric": {},
            "chart-top-destinations": { place: y },
            "chart-category-donut": { category: label },
            "chart-monthly-trend": { month: x },
            "chart-seasonal-distribution": { season: x },
            "chart-recommendation-pie": { recommended: label },
            "chart-geo-top-states": { state: y },
            "chart-geo-cat-state": { state: x, category: traceName },
            "chart-geo-location-types": { location_type: x },
            "chart-demo-age": { age_group: x },
            "chart-demo-gender": { gender: label },
            "chart-demo-group": { travel_group: x },
            "chart-demo-heatmap": { age_group: y, travel_group: x },
            "chart-fin-cat-cost": { category: x },
            "chart-fin-state-cost": { state: y },
            "chart-rev-top-dest": { place: y }
        };
        const selection = mappings[chartId];

        if (chartId === "chart-segment-metric") {
            const dimension = document.getElementById("explorer-dimension").value;
            const dimensionKeys = {
                Destination: "place", State: "state", Category: "category", Season: "season",
                "Travel group": "travel_group", "Age group": "age_group"
            };
            const key = dimensionKeys[dimension];
            return key ? { [key]: x } : null;
        }

        if (chartId === "chart-rev-words") return y ? { review_keyword: y } : null;

        if (chartId === "chart-perf-scatter" && custom[0]) return { place: String(custom[0]) };
        if (chartId === "chart-fin-cost-vs-stay" && custom[0]) return { place: String(custom[0]) };
        return selection || null;
    },

    /**
     * Render or update a Plotly figure in a container element.
     * @param {string} containerId - DOM ID of the container element
     * @param {Object} figure - Plotly figure dictionary with data and layout
     */
    render: function(containerId, figure) {
        const el = document.getElementById(containerId);
        if (!el || !figure || !figure.data) {
            return;
        }

        const data = figure.data || [];
        const layout = figure.layout || {};

        // Ensure modern font and responsive defaults
        layout.autosize = true;
        layout.clickmode = "event+select";
        layout.margin = layout.margin || { l: 40, r: 30, t: 40, b: 40 };
        layout.font = layout.font || {};
        layout.font.family = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif";

        const config = {
            responsive: true,
            displayModeBar: false,
            displaylogo: false
        };

        Plotly.newPlot(el, data, layout, config).then(() => {
            if (typeof el.removeAllListeners === "function") el.removeAllListeners("plotly_click");
            el.on("plotly_click", event => {
                if (!this.selectionHandler || !event.points || !event.points.length) return;
                const selection = this.selectionForPoint(containerId, event.points[0]);
                if (selection) this.selectionHandler(selection);
            });
        });
    },

    /**
     * Trigger responsive resize across all active Plotly chart containers.
     */
    resizeAll: function() {
        const containers = document.querySelectorAll('.chart-container');
        containers.forEach(function(el) {
            if (el && el.data) {
                Plotly.Plots.resize(el);
            }
        });
    }
};

// Automatic window resize listener
window.addEventListener('resize', function() {
    Charts.resizeAll();
});

