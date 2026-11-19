/**
 * India Tourism Analytics & BI Dashboard
 * Main Application Orchestrator
 */

const App = {
    currentSection: "overview",
    metadata: {
        states: [],
        categories: [],
        seasons: [],
        travel_groups: [],
        destinations: []
    },
    latestRecommendations: [],
    chartFilters: {},

    pageHeaders: {
        overview: {
            title: "Executive Overview Dashboard",
            subtitle: "High-level tourism performance, geographical volume, category mix, and seasonal patterns"
        },
        geographical: {
            title: "Geographical Tourism Analysis",
            subtitle: "Explore tourism destinations, state-wise distribution and geographical patterns across India."
        },
        demographics: {
            title: "Tourist Demographics & Persona Analysis",
            subtitle: "Behavioral profiling across age cohorts, gender identities, travel party compositions, and seasonal demand"
        },
        performance: {
            title: "Destination Performance & Quality Benchmarks",
            subtitle: "Evaluating tourist satisfaction, popularity indices, cleanliness, safety, and accessibility standards"
        },
        financial: {
            title: "Financial & Travel Expense Analysis",
            subtitle: "Travel cost distribution, state expenditures, cost elasticity, and interactive budget simulator"
        },
        reviews: {
            title: "Tourist Review & Text Analytics",
            subtitle: "VADER sentiment classification, frequent keyword themes, and visitor transcript explorer"
        },
        recommender: {
            title: "Smart Recommender, Destination Battle & 3D Analytics",
            subtitle: "Algorithmic Multi-Criteria Decision Analysis (MCDA), Head-to-Head Benchmarking, and 3D Opportunity Space"
        },
        map: {
            title: "Interactive Hierarchical GIS Map",
            subtitle: "Browse the prototype directory: India ➔ State ➔ District ➔ Destination"
        }
    },

    /**
     * Initialize Application
     */
    init: function() {
        window.App = this;
        Charts.setSelectionHandler(selection => this.applyChartSelection(selection));
        this.bindEvents();
        this.fetchFilterMetadata().then(() => {
            this.loadCurrentSection();
        });
    },

    /**
     * Bind DOM Event Handlers
     */
    bindEvents: function() {
        // Navigation clicks
        document.querySelectorAll(".nav-item").forEach(item => {
            item.addEventListener("click", (e) => {
                e.preventDefault();
                const target = item.getAttribute("data-section");
                this.switchSection(target);
            });
        });

        // Mobile sidebar toggle
        const toggleBtn = document.getElementById("toggle-sidebar");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                document.getElementById("sidebar").classList.toggle("open");
            });
        }

        // Sidebar filters
        document.getElementById("filter-rating").addEventListener("input", (e) => {
            document.getElementById("label-rating-val").textContent = parseFloat(e.target.value).toFixed(1);
        });

        document.getElementById("btn-apply-filters").addEventListener("click", () => {
            this.loadCurrentSection();
        });

        document.getElementById("btn-reset-filters").addEventListener("click", () => {
            this.resetFilters();
            this.loadCurrentSection();
        });

        document.getElementById("btn-clear-chart-filters").addEventListener("click", () => {
            this.chartFilters = {};
            MapEngine.geoSelectedPlace = "";
            const reviewSearch = document.getElementById("review-keyword-input");
            if (reviewSearch) reviewSearch.value = "";
            this.updateChartFilterSummary();
            this.loadCurrentSection();
        });

        // Viva Presets
        document.querySelectorAll(".preset-pill").forEach(pill => {
            pill.addEventListener("click", (e) => {
                const preset = pill.getAttribute("data-preset");
                this.applyPreset(preset);
            });
        });

        // Segment Metric Explorer
        document.getElementById("explorer-dimension").addEventListener("change", () => this.updateSegmentMetric());
        document.getElementById("explorer-metric").addEventListener("change", () => this.updateSegmentMetric());

        // Financial Budget Matcher Slider
        const budgetSlider = document.getElementById("budget-matcher-slider");
        if (budgetSlider) {
            budgetSlider.addEventListener("input", (e) => {
                document.getElementById("budget-matcher-val").textContent = `₹${parseInt(e.target.value).toLocaleString()}`;
            });
            budgetSlider.addEventListener("change", () => {
                this.updateBudgetMatcher();
            });
        }

        // Financial Custom Estimator
        const estInputs = ["estimator-destination", "estimator-travelers", "estimator-days", "estimator-tier"];
        estInputs.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener("change", () => this.updateTripEstimator());
        });

        // Review Search Engine
        const revDest = document.getElementById("review-dest-filter");
        const revKw = document.getElementById("review-keyword-input");
        if (revDest) revDest.addEventListener("change", () => this.updateReviewSearch());
        if (revKw) {
            let debounceTimer;
            revKw.addEventListener("input", () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => this.updateReviewSearch(), 300);
            });
        }

        // Subtabs for Recommender
        document.querySelectorAll(".sub-tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".sub-tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".subtab-content").forEach(c => c.classList.remove("active"));

                btn.classList.add("active");
                const subtab = btn.getAttribute("data-subtab");
                const targetContent = document.getElementById(`subtab-${subtab}`);
                if (targetContent) targetContent.classList.add("active");

                if (subtab === "battle") this.updateDestinationBattle();
                if (subtab === "3d") this.load3DOpportunitySpace();
                Charts.resizeAll();
            });
        });

        // MCDA Recommender inputs
        const mcdaInputs = ["mcda-theme", "mcda-party", "mcda-budget", "mcda-season"];
        mcdaInputs.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener("input", () => {
                    if (id === "mcda-budget") {
                        document.getElementById("mcda-budget-label").textContent = `₹${parseInt(el.value).toLocaleString()}`;
                    }
                });
                el.addEventListener("change", () => this.updateMCDARecommendations());
            }
        });

        // Battle selectors
        const battleA = document.getElementById("battle-dest-a");
        const battleB = document.getElementById("battle-dest-b");
        if (battleA) battleA.addEventListener("change", () => this.updateDestinationBattle());
        if (battleB) battleB.addEventListener("change", () => this.updateDestinationBattle());

        const medalGrid = document.getElementById("mcda-medal-grid");
        if (medalGrid) {
            medalGrid.addEventListener("click", (event) => {
                const button = event.target.closest("[data-plan-destination], [data-compare-destination]");
                if (!button) return;

                const destination = button.dataset.planDestination || button.dataset.compareDestination;
                if (button.hasAttribute("data-plan-destination")) {
                    document.getElementById("estimator-destination").value = destination;
                    this.switchSection("financial");
                    return;
                }

                const alternative = this.latestRecommendations.find(item => item.Place !== destination);
                if (!alternative) return;
                document.getElementById("battle-dest-a").value = destination;
                document.getElementById("battle-dest-b").value = alternative.Place;
                this.switchSection("recommender");
                document.querySelector('.sub-tab-btn[data-subtab="battle"]').click();
            });
        }
    },

    /**
     * Switch Visible Section
     */
    switchSection: function(sectionId) {
        this.currentSection = sectionId;

        // Update nav items
        document.querySelectorAll(".nav-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-section") === sectionId);
        });

        // Update sections
        document.querySelectorAll(".dashboard-section").forEach(sec => {
            sec.classList.toggle("active", sec.id === `section-${sectionId}`);
        });

        // Update header titles
        const h = this.pageHeaders[sectionId] || { title: "Dashboard", subtitle: "" };
        document.getElementById("page-title").textContent = h.title;
        document.getElementById("page-subtitle").textContent = h.subtitle;

        // Close mobile sidebar if open
        document.getElementById("sidebar").classList.remove("open");

        // Load section data
        this.loadCurrentSection();
    },

    /**
     * Collect Active Global Filters
     */
    getActiveFilters: function() {
        const stateVal = document.getElementById("filter-state").value;
        const catVal = document.getElementById("filter-category").value;
        const seasonVal = document.getElementById("filter-season").value;
        const groupVal = document.getElementById("filter-group").value;
        const minRating = parseFloat(document.getElementById("filter-rating").value);

        return {
            states: stateVal === "All" ? [] : [stateVal],
            categories: catVal === "All" ? [] : [catVal],
            seasons: seasonVal === "All" ? [] : [seasonVal],
            travel_groups: groupVal === "All" ? [] : [groupVal],
            min_rating: minRating > 1.0 ? minRating : null,
            chart_filters: this.chartFilters
        };
    },

    applyChartSelection: function(selection) {
        const keys = Object.keys(selection || {}).filter(key => selection[key] !== "");
        if (!keys.length) return;

        const isAlreadySelected = keys.every(key => this.chartFilters[key] === selection[key]);
        if (isAlreadySelected) {
            keys.forEach(key => delete this.chartFilters[key]);
        } else {
            keys.forEach(key => { this.chartFilters[key] = selection[key]; });
        }

        const reviewSearch = document.getElementById("review-keyword-input");
        if (reviewSearch && keys.includes("review_keyword")) {
            reviewSearch.value = this.chartFilters.review_keyword || "";
        }

        this.updateChartFilterSummary();
        this.loadCurrentSection();
    },

    updateChartFilterSummary: function() {
        const labels = {
            state: "State", category: "Category", season: "Season", travel_group: "Travel group",
            place: "Destination", month: "Month", age_group: "Age group", gender: "Gender",
            recommended: "Recommendation", location_type: "Setting", review_keyword: "Review keyword"
        };
        const entries = Object.entries(this.chartFilters);
        const summary = document.getElementById("chart-filter-summary");
        const clearButton = document.getElementById("btn-clear-chart-filters");
        summary.textContent = entries.length
            ? `Selected: ${entries.map(([key, value]) => `${labels[key] || key}: ${value}`).join(" · ")}`
            : "";
        clearButton.hidden = entries.length === 0;
    },

    /**
     * Reset All Filters to Defaults
     */
    resetFilters: function() {
        this.chartFilters = {};
        MapEngine.geoSelectedPlace = "";
        const reviewSearch = document.getElementById("review-keyword-input");
        if (reviewSearch) reviewSearch.value = "";
        this.updateChartFilterSummary();
        document.getElementById("filter-state").value = "All";
        document.getElementById("filter-category").value = "All";
        document.getElementById("filter-season").value = "All";
        document.getElementById("filter-group").value = "All";
        document.getElementById("filter-rating").value = 1.0;
        document.getElementById("label-rating-val").textContent = "1.0";
    },

    /**
     * Apply Preset Slicer Configurations
     */
    applyPreset: function(preset) {
        this.resetFilters();
        if (preset === "solo-adventure") {
            document.getElementById("filter-category").value = "Adventure";
            document.getElementById("filter-group").value = "Solo";
        } else if (preset === "heritage-family") {
            document.getElementById("filter-category").value = "Historical";
            document.getElementById("filter-group").value = "Family";
        } else if (preset === "south-india") {
            document.getElementById("filter-state").value = "Karnataka";
        }
        this.loadCurrentSection();
    },

    /**
     * Fetch Filter Metadata from Flask API
     */
    fetchFilterMetadata: async function() {
        try {
            const res = await fetch("/api/filters");
            const data = await res.json();
            this.metadata = data;
            const visitorCountLabel = document.getElementById("map-visitor-count");
            if (visitorCountLabel) visitorCountLabel.textContent = `${data.total_records.toLocaleString()} visitor records`;

            // Populate state dropdown
            const stateSelect = document.getElementById("filter-state");
            data.states.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s;
                opt.textContent = s;
                stateSelect.appendChild(opt);
            });

            // Populate category dropdown
            const catSelect = document.getElementById("filter-category");
            data.categories.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c;
                opt.textContent = c;
                catSelect.appendChild(opt);
            });

            // Populate season dropdown
            const seasonSelect = document.getElementById("filter-season");
            data.seasons.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s;
                opt.textContent = s;
                seasonSelect.appendChild(opt);
            });

            // Populate travel group dropdown
            const groupSelect = document.getElementById("filter-group");
            data.travel_groups.forEach(g => {
                const opt = document.createElement("option");
                opt.value = g;
                opt.textContent = g;
                groupSelect.appendChild(opt);
            });

            // Populate review destinations
            const revDest = document.getElementById("review-dest-filter");
            data.destinations.forEach(d => {
                const opt = document.createElement("option");
                opt.value = d;
                opt.textContent = d;
                revDest.appendChild(opt);
            });

            // Populate estimator destinations
            const estDest = document.getElementById("estimator-destination");
            data.destinations.forEach(d => {
                const opt = document.createElement("option");
                opt.value = d;
                opt.textContent = d;
                estDest.appendChild(opt);
            });

            // Populate battle destinations
            const battleA = document.getElementById("battle-dest-a");
            const battleB = document.getElementById("battle-dest-b");
            data.destinations.forEach((d, idx) => {
                const optA = document.createElement("option");
                optA.value = d;
                optA.textContent = d;
                battleA.appendChild(optA);

                const optB = document.createElement("option");
                optB.value = d;
                optB.textContent = d;
                if (idx === 1) optB.selected = true;
                battleB.appendChild(optB);
            });

        } catch (err) {
            console.error("Filter metadata fetch error:", err);
        }
    },

    /**
     * Dispatcher to Load Active Section
     */
    loadCurrentSection: function() {
        switch (this.currentSection) {
            case "overview":
                this.loadOverview();
                break;
            case "geographical":
                this.loadGeographical();
                break;
            case "demographics":
                this.loadDemographics();
                break;
            case "performance":
                this.loadPerformance();
                break;
            case "financial":
                this.loadFinancial();
                break;
            case "reviews":
                this.loadReviews();
                break;
            case "recommender":
                this.loadRecommender();
                break;
            case "map":
                this.loadMap();
                break;
        }
    },

    /**
     * Update Record Count in Slicer Header
     */
    updateRecordCount: function(cnt) {
        document.getElementById("badge-record-count").textContent = cnt.toLocaleString();
    },

    // ---------------------------------------------------------
    // 1. EXECUTIVE OVERVIEW
    // ---------------------------------------------------------
    loadOverview: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/overview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count);

        // KPIs
        const k = data.kpis;
        document.getElementById("kpi-total-records").textContent = k.total_records.toLocaleString();
        document.getElementById("kpi-total-states").textContent = k.total_states;
        document.getElementById("kpi-total-dest").textContent = k.unique_destinations;
        document.getElementById("kpi-avg-rating").textContent = `⭐ ${k.avg_rating}`;
        document.getElementById("kpi-avg-cost").textContent = `₹${k.avg_cost.toLocaleString()}`;
        document.getElementById("kpi-avg-stay").textContent = `${k.avg_stay} Days`;
        document.getElementById("kpi-recommendation-pct").textContent = `${k.recommendation_pct}%`;

        // Narrative Callout
        const n = data.narrative;
        if (n && n.top_state) {
            document.getElementById("overview-narrative-content").innerHTML = `
                <strong>${n.top_state}</strong> leads with the highest concentration of tourist records under current filter selections (${n.top_state_count} records; ${n.top_state_pct}% of active cohort). 
                <strong>${n.top_place}</strong> boasts the highest average popularity score (${n.top_place_score}/100), 
                while <strong>${n.top_category}</strong> represents the dominant tourism category (${n.top_category_share}%).
            `;
        } else {
            document.getElementById("overview-narrative-content").textContent =
                "No visitor records match the current filters. Clear the chart selection or broaden the filters to see the overview.";
        }

        // Charts
        const c = data.charts;
        Charts.render("chart-state-volume", c.state_volume);
        Charts.render("chart-top-destinations", c.top_destinations);
        Charts.render("chart-category-donut", c.category_donut);
        Charts.render("chart-monthly-trend", c.monthly_trend);
        Charts.render("chart-seasonal-distribution", c.seasonal_distribution);
        Charts.render("chart-recommendation-pie", c.recommendation_pie);

        this.updateSegmentMetric();
    },

    updateSegmentMetric: async function() {
        const dim = document.getElementById("explorer-dimension").value;
        const metric = document.getElementById("explorer-metric").value;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/overview/segment-metric", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ dimension: dim, metric: metric, filters })
        });
        const data = await res.json();
        Charts.render("chart-segment-metric", data.chart);
    },

    // ---------------------------------------------------------
    // 2. GEOGRAPHICAL ANALYSIS
    // ---------------------------------------------------------
    loadGeographical: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/geographical", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count);

        // KPIs
        const k = data.kpis;
        document.getElementById("geo-kpi-states").textContent = k.total_states;
        document.getElementById("geo-kpi-dest").textContent = k.total_destinations;
        document.getElementById("geo-kpi-top-state").textContent = k.top_state;
        document.getElementById("geo-kpi-top-state-sub").textContent = `${k.top_state_records} records (${k.top_state_share}%)`;
        document.getElementById("geo-kpi-top-cat").textContent = k.top_category;
        document.getElementById("geo-kpi-top-cat-sub").textContent = `${k.top_category_records} records (${k.top_category_share}%)`;

        // Render Leaflet Map
        MapEngine.initGeographicalMap(data.markers);

        // Charts
        const c = data.charts;
        Charts.render("chart-geo-top-states", c.top_states);
        Charts.render("chart-geo-cat-state", c.category_by_state);
        Charts.render("chart-geo-location-types", c.location_types);
    },

    // ---------------------------------------------------------
    // 3. TOURIST DEMOGRAPHICS
    // ---------------------------------------------------------
    loadDemographics: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/demographics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count);

        // KPIs
        const k = data.kpis;
        document.getElementById("demo-kpi-age").textContent = k.dominant_age;
        document.getElementById("demo-kpi-age-sub").textContent = `${k.dominant_age_count} travelers (${k.dominant_age_pct}%)`;
        document.getElementById("demo-kpi-group").textContent = k.primary_group;
        document.getElementById("demo-kpi-group-sub").textContent = `${k.primary_group_count} bookings (${k.primary_group_pct}%)`;
        document.getElementById("demo-kpi-gender").textContent = k.leading_gender;
        document.getElementById("demo-kpi-gender-sub").textContent = `${k.leading_gender_count} respondents (${k.leading_gender_pct}%)`;
        document.getElementById("demo-kpi-solo").textContent = `${k.solo_ratio}%`;

        // Charts
        const c = data.charts;
        Charts.render("chart-demo-age", c.age_distribution);
        Charts.render("chart-demo-gender", c.gender_breakdown);
        Charts.render("chart-demo-group", c.travel_group_dynamics);
        Charts.render("chart-demo-heatmap", c.age_vs_travel_heatmap);
    },

    // ---------------------------------------------------------
    // 4. TOURISM PERFORMANCE
    // ---------------------------------------------------------
    loadPerformance: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/performance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count);

        // KPIs
        const k = data.kpis;
        document.getElementById("perf-kpi-top-rated").textContent = k.top_rated_place;
        document.getElementById("perf-kpi-top-rated-sub").textContent = `⭐ ${k.top_rated_val}/5.0 (${k.top_rated_state})`;
        document.getElementById("perf-kpi-most-pop").textContent = k.most_popular_place;
        document.getElementById("perf-kpi-most-pop-sub").textContent = `Score: ${k.most_popular_val}/100`;
        document.getElementById("perf-kpi-clean").textContent = `${k.avg_cleanliness} / 5.0`;
        document.getElementById("perf-kpi-safety").textContent = `${k.avg_safety} / 5.0`;

        // Charts
        const c = data.charts;
        Charts.render("chart-perf-scatter", c.scatter_matrix);
        Charts.render("chart-perf-radar", c.quality_radar);

        // Benchmark table
        const tbody = document.querySelector("#table-performance-rankings tbody");
        tbody.innerHTML = "";
        (c.benchmark_table || []).forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${row.Place}</strong></td>
                <td>${row.State}</td>
                <td><span style="font-weight:600;color:#0284c7;">${row.Category}</span></td>
                <td>⭐ ${row.Avg_Rating}</td>
                <td>${row.Popularity_Score}</td>
                <td>${row.Cleanliness}</td>
                <td>${row.Safety}</td>
                <td>${row.Accessibility}</td>
                <td>${row.Advocacy}%</td>
                <td>${row.Records}</td>
            `;
            tbody.appendChild(tr);
        });
    },

    // ---------------------------------------------------------
    // 5. FINANCIAL ANALYSIS
    // ---------------------------------------------------------
    loadFinancial: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/financial", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count);

        // KPIs
        const k = data.kpis;
        document.getElementById("fin-kpi-avg-cost").textContent = `₹${k.avg_cost.toLocaleString()}`;
        document.getElementById("fin-kpi-min-cost").textContent = `₹${k.min_cost.toLocaleString()}`;
        document.getElementById("fin-kpi-max-cost").textContent = `₹${k.max_cost.toLocaleString()}`;
        document.getElementById("fin-kpi-daily-burn").textContent = `₹${k.daily_burn.toLocaleString()} / day`;
        document.getElementById("fin-kpi-daily-burn-sub").textContent = `Based on ${k.avg_stay} days avg stay`;

        // Charts
        const c = data.charts;
        Charts.render("chart-fin-cat-cost", c.cost_by_category);
        Charts.render("chart-fin-state-cost", c.cost_by_state);
        Charts.render("chart-fin-cost-vs-stay", c.cost_vs_stay);

        // Category Extremes table
        const tbody = document.querySelector("#table-category-extremes tbody");
        tbody.innerHTML = "";
        (c.category_extremes || []).forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${row.Category}</strong></td>
                <td>₹${row.Min_Cost.toLocaleString()}</td>
                <td style="font-weight:700; color:#0284c7;">₹${row.Avg_Cost.toLocaleString()}</td>
                <td>₹${row.Median_Cost.toLocaleString()}</td>
                <td>₹${row.Max_Cost.toLocaleString()}</td>
                <td>${row.Records}</td>
            `;
            tbody.appendChild(tr);
        });

        // Initialize Budget Matcher & Estimator
        this.updateBudgetMatcher();
        this.updateTripEstimator();
    },

    updateBudgetMatcher: async function() {
        const slider = document.getElementById("budget-matcher-slider");
        const budget = slider ? slider.value : 3000;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/financial/budget-matcher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ max_budget: budget, filters })
        });
        const data = await res.json();

        document.getElementById("budget-matched-count").textContent = `${data.count} Places`;
        document.getElementById("budget-matched-sub").textContent = `Within ₹${parseInt(budget).toLocaleString()} budget`;
        document.getElementById("budget-cheapest-place").textContent = data.cheapest_place || "None";
        document.getElementById("budget-cheapest-cost").textContent = data.cheapest_cost ? `Avg cost: ₹${data.cheapest_cost.toLocaleString()}` : "N/A";

        const tbody = document.querySelector("#table-budget-results tbody");
        tbody.innerHTML = "";
        (data.results || []).forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${row.Place}</strong></td>
                <td>${row.State}</td>
                <td>${row.Category}</td>
                <td style="font-weight:700; color:#10b981;">₹${row.Avg_Cost.toLocaleString()}</td>
                <td>₹${row.Min_Cost.toLocaleString()}</td>
                <td>₹${row.Max_Cost.toLocaleString()}</td>
                <td>⭐ ${row.Avg_Rating}</td>
                <td>${row.Avg_Stay}</td>
                <td>${row.Records}</td>
            `;
            tbody.appendChild(tr);
        });
    },

    updateTripEstimator: async function() {
        const dest = document.getElementById("estimator-destination").value;
        const travelers = document.getElementById("estimator-travelers").value;
        const days = document.getElementById("estimator-days").value;
        const tier = document.getElementById("estimator-tier").value;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/financial/cost-estimator", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                destination: dest,
                num_travelers: travelers,
                trip_days: days,
                comfort_tier: tier,
                filters
            })
        });
        const data = await res.json();

        document.getElementById("est-total-cost").textContent = `₹${data.total_projected.toLocaleString()}`;
        document.getElementById("est-desc").textContent = `For ${data.num_travelers} traveler(s) for ${data.trip_days} day(s) at ${data.destination} (${data.comfort_tier})`;
        document.getElementById("est-cost-per-person").textContent = `₹${data.cost_per_person.toLocaleString()}`;
        document.getElementById("est-daily-per-person").textContent = `₹${data.daily_per_person.toLocaleString()}/day`;
    },

    // ---------------------------------------------------------
    // 6. REVIEW ANALYTICS
    // ---------------------------------------------------------
    loadReviews: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/reviews", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        this.updateRecordCount(data.filtered_count || 0);

        // KPIs
        const k = data.kpis;
        document.getElementById("rev-kpi-total").textContent = k.total_reviews.toLocaleString();
        document.getElementById("rev-kpi-pos").textContent = `${k.pos_pct}%`;
        document.getElementById("rev-kpi-pos-sub").textContent = `${k.pos_cnt} reviews (≥ +0.05)`;
        document.getElementById("rev-kpi-neu").textContent = `${k.neu_pct}%`;
        document.getElementById("rev-kpi-neu-sub").textContent = `${k.neu_cnt} reviews (-0.05 to +0.05)`;
        document.getElementById("rev-kpi-neg").textContent = `${k.neg_pct}%`;
        document.getElementById("rev-kpi-neg-sub").textContent = `${k.neg_cnt} reviews (≤ -0.05)`;

        // Charts
        const c = data.charts;
        Charts.render("chart-rev-words", c.word_frequency);
        Charts.render("chart-rev-sentiment", c.sentiment_doughnut);
        Charts.render("chart-rev-top-dest", c.top_dest_reviews);

        this.updateReviewSearch();
    },

    updateReviewSearch: async function() {
        const dest = document.getElementById("review-dest-filter").value;
        const kw = document.getElementById("review-keyword-input").value;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/reviews/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ place: dest, keyword: kw, filters })
        });
        const data = await res.json();

        document.getElementById("reviews-matched-count").textContent = data.count.toLocaleString();
        const tbody = document.querySelector("#table-review-explorer tbody");
        tbody.innerHTML = "";

        data.reviews.forEach(r => {
            const tr = document.createElement("tr");
            const sentColor = r.Sentiment === "Positive" ? "#10b981" : (r.Sentiment === "Negative" ? "#ef4444" : "#6366f1");
            tr.innerHTML = `
                <td><code>${r.Visitor_ID}</code></td>
                <td><strong>${r.Place}</strong></td>
                <td>${r.State}</td>
                <td>⭐ ${r.Rating}</td>
                <td><span style="font-weight:700; color:${sentColor};">${r.Sentiment}</span></td>
                <td>${r.Polarity_Score >= 0 ? '+' : ''}${r.Polarity_Score}</td>
                <td><span style="font-style:italic;">"${r.Review}"</span></td>
            `;
            tbody.appendChild(tr);
        });
    },

    // ---------------------------------------------------------
    // 7. AI RECOMMENDER & BATTLE
    // ---------------------------------------------------------
    loadRecommender: function() {
        this.updateMCDARecommendations();
        this.updateDestinationBattle();
        this.load3DOpportunitySpace();
    },

    updateMCDARecommendations: async function() {
        const theme = document.getElementById("mcda-theme").value;
        const party = document.getElementById("mcda-party").value;
        const budget = document.getElementById("mcda-budget").value;
        const season = document.getElementById("mcda-season").value;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/recommender", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ theme, party, budget, season, filters })
        });
        const data = await res.json();
        const recs = data.recommendations || [];
        this.latestRecommendations = recs;

        // Render Top 3 Medal Cards
        const top3 = recs.slice(0, 3);
        const medalGrid = document.getElementById("mcda-medal-grid");
        medalGrid.innerHTML = "";

        const medals = ["🥇 Best Match", "🥈 Top Alternative", "🥉 Value Pick"];
        const accents = ["#0284c7", "#10b981", "#f97316"];

        if (!recs.length) {
            medalGrid.innerHTML = '<div class="chart-empty-message">No destinations match the current filters and preferences. Broaden the filters or choose another preference.</div>';
        }

        top3.forEach((item, idx) => {
            const card = document.createElement("div");
            card.className = "medal-card";
            card.style.setProperty("--card-accent", accents[idx]);
            card.innerHTML = `
                <div class="medal-card-header">
                    <span class="medal-label">${medals[idx]}</span>
                    <span class="match-badge">${item.Match_Score}% MATCH</span>
                </div>
                <div class="medal-place">${item.Place}</div>
                <div class="medal-meta">📍 ${item.State} • <strong>${item.Category}</strong> (${item.Location_Type})</div>
                <div class="medal-stats">
                    <div><strong>Avg Rating:</strong> ⭐ ${item.Avg_Rating}</div>
                    <div><strong>Est Cost:</strong> ₹${item.Avg_Cost.toLocaleString()}</div>
                    <div><strong>Avg Stay:</strong> ${item.Avg_Stay} Days</div>
                    <div><strong>Popularity:</strong> ${item.Popularity}/100</div>
                    <div><strong>Based on:</strong> ${item.Records.toLocaleString()} visitor records</div>
                </div>
                <div class="mcda-reasons"><strong>Why this match</strong><ul>${item.Reasons.map(reason => `<li>${this.escapeHtml(reason)}</li>`).join("")}</ul></div>
                <div class="mcda-card-actions">
                    <button class="btn btn-secondary btn-sm" type="button" data-compare-destination="${this.escapeHtml(item.Place)}">Compare</button>
                    <button class="btn btn-primary btn-sm" type="button" data-plan-destination="${this.escapeHtml(item.Place)}">Estimate trip</button>
                </div>
            `;
            medalGrid.appendChild(card);
        });

        // Full rankings table
        const tbody = document.querySelector("#table-mcda-rankings tbody");
        tbody.innerHTML = "";
        recs.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${idx + 1}</strong></td>
                <td><strong>${item.Place}</strong></td>
                <td>${item.State}</td>
                <td>${item.Category}</td>
                <td><span class="match-badge">${item.Match_Score}%</span></td>
                <td>⭐ ${item.Avg_Rating}</td>
                <td>₹${item.Avg_Cost.toLocaleString()}</td>
                <td>${item.Avg_Stay} Days</td>
                <td>${item.Popularity}</td>
                <td>${item.Records.toLocaleString()}</td>
                <td>${item.Reasons.slice(0, 2).map(reason => this.escapeHtml(reason)).join(" • ")}</td>
            `;
            tbody.appendChild(tr);
        });
    },

    escapeHtml: function(value) {
        return String(value).replace(/[&<>"']/g, character => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
        })[character]);
    },

    updateDestinationBattle: async function() {
        const destA = document.getElementById("battle-dest-a").value;
        const destB = document.getElementById("battle-dest-b").value;
        const filters = this.getActiveFilters();

        const res = await fetch("/api/battle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ dest_a: destA, dest_b: destB, filters })
        });
        const data = await res.json();
        if (!data.stats_a) return;

        // Update Radar chart
        Charts.render("chart-battle-radar", data.radar_chart);

        // Update Winner Banner
        document.getElementById("battle-verdict-banner").innerHTML = `
            <h3>🏆 Overall Benchmarking Winner: <u>${data.winner}</u></h3>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748b;">
                <strong>${data.stats_a.Place}</strong> won ${data.wins_a} categories &bull; 
                <strong>${data.stats_b.Place}</strong> won ${data.wins_b} categories.
            </p>
        `;

        // Update Scorecard table
        document.getElementById("th-battle-a").textContent = data.stats_a.Place;
        document.getElementById("th-battle-b").textContent = data.stats_b.Place;

        const tbody = document.querySelector("#table-battle-scorecard tbody");
        tbody.innerHTML = "";

        const attrs = [
            { name: "Average Satisfaction (Rating)", valA: `⭐ ${data.stats_a.Rating}`, valB: `⭐ ${data.stats_b.Rating}`, win: data.stats_a.Rating > data.stats_b.Rating ? data.stats_a.Place : data.stats_b.Place },
            { name: "Popularity Index (0-100)", valA: `${data.stats_a.Popularity}`, valB: `${data.stats_b.Popularity}`, win: data.stats_a.Popularity > data.stats_b.Popularity ? data.stats_a.Place : data.stats_b.Place },
            { name: "Budget Affordability (Cost)", valA: `₹${data.stats_a.Cost.toLocaleString()}`, valB: `₹${data.stats_b.Cost.toLocaleString()}`, win: data.stats_a.Cost < data.stats_b.Cost ? data.stats_a.Place : data.stats_b.Place },
            { name: "Cleanliness Index (0-5)", valA: `${data.stats_a.Cleanliness}`, valB: `${data.stats_b.Cleanliness}`, win: data.stats_a.Cleanliness > data.stats_b.Cleanliness ? data.stats_a.Place : data.stats_b.Place },
            { name: "Safety Index (0-5)", valA: `${data.stats_a.Safety}`, valB: `${data.stats_b.Safety}`, win: data.stats_a.Safety > data.stats_b.Safety ? data.stats_a.Place : data.stats_b.Place },
            { name: "Accessibility Index (0-5)", valA: `${data.stats_a.Accessibility}`, valB: `${data.stats_b.Accessibility}`, win: data.stats_a.Accessibility > data.stats_b.Accessibility ? data.stats_a.Place : data.stats_b.Place },
            { name: "Advocacy Recommendation %", valA: `${data.stats_a.Advocacy}%`, valB: `${data.stats_b.Advocacy}%`, win: data.stats_a.Advocacy > data.stats_b.Advocacy ? data.stats_a.Place : data.stats_b.Place }
        ];

        attrs.forEach(a => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${a.name}</strong></td>
                <td>${a.valA}</td>
                <td>${a.valB}</td>
                <td><span style="font-weight:700; color: ${a.win === data.stats_a.Place ? '#0284c7' : '#f97316'};">${a.win}</span></td>
            `;
            tbody.appendChild(tr);
        });
    },

    load3DOpportunitySpace: async function() {
        const filters = this.getActiveFilters();
        const res = await fetch("/api/3d-space", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filters })
        });
        const data = await res.json();
        Charts.render("chart-3d-space", data.chart);
    },

    // ---------------------------------------------------------
    // 8. HIERARCHICAL GIS MAP
    // ---------------------------------------------------------
    loadMap: function() {
        MapEngine.initHierarchicalMap();
    }
};

// Initialize application on DOM ready
document.addEventListener("DOMContentLoaded", () => {
    App.init();
});

