/**
 * Charts Rendering Module (Plotly.js Bridge)
 * Handles client-side rendering and responsive resizing of Plotly charts
 * received from Flask API backend.
 */

const Charts = {
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
        layout.margin = layout.margin || { l: 40, r: 30, t: 40, b: 40 };
        layout.font = layout.font || {};
        layout.font.family = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif";

        const config = {
            responsive: true,
            displayModeBar: false,
            displaylogo: false
        };

        Plotly.newPlot(el, data, layout, config);
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

