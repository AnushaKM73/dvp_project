/**
 * Leaflet GIS Maps Module
 * Manages:
 * 1. Geographical Analysis Map (category-colored pins, hover tooltips, click popups).
 * 2. 3-Level Hierarchical GIS Map (India -> State Districts -> District Tourist Places).
 */

const MapEngine = {
    geoMap: null,
    geoMarkersLayer: null,
    geoBoundaryLayer: null,

    hierMap: null,
    hierCurrentLayer: null,
    hierPinsLayer: null,
    hierLevel: "india", // "india" | "state" | "district"
    selectedState: "",
    selectedDistrict: "",
    destinationsList: [],
    districtMap: {},

    INDIA_CDN_URL: "https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/india.geojson",

    // Canonical district aliases for historical & newly split districts
    DISTRICT_ALIASES: {
        "ballari": ["vijayanagara", "bellary"],
        "bellary": ["vijayanagara", "ballari"],
        "vijayanagara": ["ballari", "bellary"],
        "mysuru": ["mysore"],
        "mysore": ["mysuru"],
        "kodagu": ["coorg", "madikeri"],
        "coorg": ["kodagu"],
        "bengaluru urban": ["bengaluru urban", "bangalore urban"],
        "bengaluru rural": ["bengaluru rural", "bangalore rural"],
        "mumbai city": ["mumbai"],
        "south andaman": ["port blair", "andaman"]
    },

    /**
     * Helper: Extract state name from feature properties
     */
    getStateName: function(feature) {
        const p = feature.properties || {};
        return (
            p.st_nm || p.ST_NM || p.STATE || p.State_Name ||
            p.state || p.name || p.NAME_1 || p.NAME || "Unknown"
        );
    },

    /**
     * Helper: Extract district name from feature properties
     */
    getDistrictName: function(feature) {
        const p = feature.properties || {};
        return (
            p.district || p.DISTRICT || p.DTNAME || p.dtname ||
            p.Dist_Name || p.District || p.name || p.NAME_2 || "Unknown District"
        );
    },

    /**
     * Normalize names for robust district matching
     */
    normalizeName: function(name) {
        return String(name || "").toLowerCase().replace(/[^a-z0-9]/g, "").trim();
    },

    /**
     * -------------------------------------------------------------
     * 1. GEOGRAPHICAL ANALYSIS MAP
     * -------------------------------------------------------------
     */
    initGeographicalMap: function(markers) {
        const container = document.getElementById("geographical-map");
        if (!container) return;

        if (!this.geoMap) {
            this.geoMap = L.map("geographical-map", {
                zoomControl: true,
                attributionControl: false
            }).setView([22.5, 79.5], 4.5);

            // Load India outline boundary for high contrast
            fetch("/api/map/geojson/india")
                .then(r => r.ok ? r.json() : fetch(this.INDIA_CDN_URL).then(res => res.json()))
                .then(geoData => {
                    this.geoBoundaryLayer = L.geoJSON(geoData, {
                        style: {
                            fillColor: "#f8fafc",
                            color: "#94a3b8",
                            weight: 1.2,
                            fillOpacity: 0.8
                        }
                    }).addTo(this.geoMap);
                    this.geoMap.fitBounds(this.geoBoundaryLayer.getBounds(), { padding: [15, 15] });
                })
                .catch(err => console.log("Geo map boundary fallback:", err));
        }

        // Clear existing markers
        if (this.geoMarkersLayer) {
            this.geoMap.removeLayer(this.geoMarkersLayer);
        }

        this.geoMarkersLayer = L.layerGroup().addTo(this.geoMap);

        const bounds = [];
        markers.forEach(m => {
            if (!m.lat || !m.lon) return;

            const latLng = [m.lat, m.lon];
            bounds.push(latLng);

            const circle = L.circleMarker(latLng, {
                radius: 8,
                fillColor: m.category_color || "#0284c7",
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.95
            });

            // Tooltip on hover
            circle.bindTooltip(`<strong>${m.place}</strong><br><span style="font-size:11px;color:#64748b;">${m.category} • ${m.state}</span>`, {
                direction: 'top',
                offset: [0, -6]
            });

            // Rich popup on click
            const popupHtml = `
                <div style="font-family: Inter, sans-serif; min-width: 220px; padding: 2px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                        <span style="font-size: 10px; font-weight:800; text-transform:uppercase; color:${m.category_color};">${m.category}</span>
                        <span style="font-size: 12px; font-weight:700; color:#f59e0b;">⭐ ${m.rating}</span>
                    </div>
                    <h4 style="margin: 0 0 2px 0; font-size: 15px; font-weight: 800; color: #0f172a;">${m.place}</h4>
                    <p style="margin: 0 0 8px 0; font-size: 11.5px; color: #64748b;">📍 ${m.state} (${m.location_type || 'Landmark'})</p>
                    <hr style="border:0; border-top:1px solid #e2e8f0; margin: 6px 0;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 11.5px; margin-bottom: 6px;">
                        <div><strong>Est. Cost:</strong> ₹${m.cost ? m.cost.toLocaleString() : 'N/A'}</div>
                        <div><strong>Avg Stay:</strong> ${m.stay} Days</div>
                        <div><strong>Best Time:</strong> ${m.best_time || 'All Year'}</div>
                        <div><strong>Visitors:</strong> ${m.visitors ? m.visitors.toLocaleString() : 'N/A'}</div>
                    </div>
                    ${m.address ? `<div style="font-size:10.5px; color:#94a3b8; border-top:1px solid #f1f5f9; padding-top:4px;">${m.address}</div>` : ''}
                </div>
            `;
            circle.bindPopup(popupHtml);

            this.geoMarkersLayer.addLayer(circle);
        });

        setTimeout(() => {
            this.geoMap.invalidateSize();
            if (bounds.length > 0) {
                this.geoMap.fitBounds(bounds, { padding: [30, 30] });
            }
        }, 200);
    },

    /**
     * -------------------------------------------------------------
     * 2. HIERARCHICAL 3-LEVEL GIS MAP
     * -------------------------------------------------------------
     */
    initHierarchicalMap: function() {
        const container = document.getElementById("hierarchical-leaflet-map");
        if (!container) return;

        if (!this.hierMap) {
            this.hierMap = L.map("hierarchical-leaflet-map", {
                zoomControl: true,
                attributionControl: false
            }).setView([22.5, 79], 4.5);

            this.hierPinsLayer = L.layerGroup().addTo(this.hierMap);

            // Fetch destination list for district matching
            fetch("/api/map/destinations")
                .then(r => r.json())
                .then(data => {
                    this.destinationsList = data.destinations || [];
                    this.districtMap = data.district_map || {};
                })
                .catch(err => console.log("Destinations fetch error:", err));

            // Wire breadcrumbs and back buttons
            document.getElementById("btn-back-to-india").addEventListener("click", () => this.showIndia());
            document.getElementById("btn-back-to-state").addEventListener("click", () => this.showState(this.selectedState));
            document.getElementById("bc-india").addEventListener("click", () => this.showIndia());
            document.getElementById("bc-state").addEventListener("click", () => this.showState(this.selectedState));

            // Initial view
            this.showIndia();
        } else {
            setTimeout(() => {
                this.hierMap.invalidateSize();
            }, 200);
        }
    },

    /**
     * Level 1: India Map (State boundaries only)
     */
    showIndia: function() {
        this.hierLevel = "india";
        this.selectedState = "";
        this.selectedDistrict = "";

        if (this.hierCurrentLayer) {
            this.hierMap.removeLayer(this.hierCurrentLayer);
            this.hierCurrentLayer = null;
        }
        if (this.hierPinsLayer) {
            this.hierPinsLayer.clearLayers();
        }

        // Hide back buttons & district places panel
        document.getElementById("btn-back-to-india").style.display = "none";
        document.getElementById("btn-back-to-state").style.display = "none";
        document.getElementById("district-places-panel").style.display = "none";
        document.getElementById("bc-sep-state").style.display = "none";
        document.getElementById("bc-state").style.display = "none";
        document.getElementById("bc-sep-dist").style.display = "none";
        document.getElementById("bc-dist").style.display = "none";

        document.getElementById("hierarchical-map-title").textContent = "🗺️ India Interactive Tourism Explorer";
        document.getElementById("hierarchical-map-desc").textContent = "Click a state to explore its districts.";
        document.getElementById("map-pill-name").textContent = "India";

        // Load India GeoJSON
        fetch("/api/map/geojson/india")
            .then(r => r.ok ? r.json() : fetch(this.INDIA_CDN_URL).then(res => res.json()))
            .then(data => {
                if (this.hierLevel !== "india") return;

                this.hierCurrentLayer = L.geoJSON(data, {
                    style: function() {
                        return {
                            fillColor: "#3498db",
                            color: "#ffffff",
                            weight: 1.2,
                            fillOpacity: 0.82
                        };
                    },
                    onEachFeature: (feature, layer) => {
                        const stateName = this.getStateName(feature);
                        layer.bindTooltip(stateName, { sticky: true });

                        layer.on({
                            mouseover: (e) => {
                                e.target.setStyle({
                                    fillColor: "#f39c12",
                                    color: "#ffffff",
                                    weight: 2.5,
                                    fillOpacity: 0.95
                                });
                                if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                                    e.target.bringToFront();
                                }
                            },
                            mouseout: (e) => {
                                if (this.hierCurrentLayer) {
                                    this.hierCurrentLayer.resetStyle(e.target);
                                }
                            },
                            click: (e) => {
                                L.DomEvent.stopPropagation(e);
                                this.showState(stateName);
                            }
                        });
                    }
                }).addTo(this.hierMap);

                this.hierMap.invalidateSize();
                this.hierMap.fitBounds(this.hierCurrentLayer.getBounds(), { padding: [15, 15] });
            })
            .catch(err => {
                console.error("India map load error:", err);
            });
    },

    /**
     * Helper: Convert state name to slug matching local files & CDN
     */
    getStateSlug: function(name) {
        const special = {
            "Andaman and Nicobar": "andaman-and-nicobar-islands",
            "Andaman and Nicobar Islands": "andaman-and-nicobar-islands",
            "Jammu and Kashmir": "jammu-and-kashmir",
            "Delhi": "delhi",
            "NCT of Delhi": "delhi",
            "Dadra and Nagar Haveli and Daman and Diu": "daman-and-diu"
        };
        if (special[name]) return special[name];
        return name.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    },

    /**
     * Level 2: State Districts Map (e.g. Karnataka)
     */
    showState: function(stateName) {
        this.hierLevel = "state";
        this.selectedState = stateName;
        this.selectedDistrict = "";

        if (this.hierCurrentLayer) {
            this.hierMap.removeLayer(this.hierCurrentLayer);
            this.hierCurrentLayer = null;
        }
        if (this.hierPinsLayer) {
            this.hierPinsLayer.clearLayers();
        }

        // Update UI
        document.getElementById("btn-back-to-india").style.display = "inline-flex";
        document.getElementById("btn-back-to-state").style.display = "none";
        document.getElementById("district-places-panel").style.display = "none";
        
        document.getElementById("bc-sep-state").style.display = "inline";
        const bcState = document.getElementById("bc-state");
        bcState.style.display = "inline";
        bcState.textContent = stateName;
        document.getElementById("bc-sep-dist").style.display = "none";
        document.getElementById("bc-dist").style.display = "none";

        document.getElementById("hierarchical-map-title").textContent = `🗺️ ${stateName} District Explorer`;
        document.getElementById("hierarchical-map-desc").textContent = "Hover over a district to see its name. Click a district to explore tourist destinations.";
        document.getElementById("map-pill-name").textContent = stateName;

        const slug = this.getStateSlug(stateName);
        const localUrl = `/api/map/geojson/${slug}`;
        const cdnUrl = `https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/states/${slug}.geojson`;

        fetch(localUrl)
            .then(r => r.ok ? r.json() : fetch(cdnUrl).then(res => res.json()))
            .then(data => {
                if (this.hierLevel !== "state" && this.hierLevel !== "district") return;

                this.hierCurrentLayer = L.geoJSON(data, {
                    style: function() {
                        return {
                            fillColor: "#3498db",
                            color: "#ffffff",
                            weight: 1.2,
                            fillOpacity: 0.85
                        };
                    },
                    onEachFeature: (feature, layer) => {
                        const distName = this.getDistrictName(feature);
                        layer.bindTooltip(distName, { sticky: true });

                        layer.on({
                            mouseover: (e) => {
                                e.target.setStyle({
                                    fillColor: "#f39c12",
                                    color: "#ffffff",
                                    weight: 2.5,
                                    fillOpacity: 0.98
                                });
                                if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                                    e.target.bringToFront();
                                }
                            },
                            mouseout: (e) => {
                                if (this.hierCurrentLayer) {
                                    this.hierCurrentLayer.resetStyle(e.target);
                                }
                            },
                            click: (e) => {
                                L.DomEvent.stopPropagation(e);
                                this.showDistrict(stateName, distName, layer);
                            }
                        });
                    }
                }).addTo(this.hierMap);

                this.hierMap.invalidateSize();
                this.hierMap.fitBounds(this.hierCurrentLayer.getBounds(), { padding: [25, 25] });
            })
            .catch(err => {
                console.error("State GeoJSON load error:", err);
                alert(`Could not load district boundaries for ${stateName}.`);
                this.showIndia();
            });
    },

    /**
     * Level 3: District Tourist Destinations
     */
    showDistrict: function(stateName, distName, districtLayer) {
        this.hierLevel = "district";
        this.selectedDistrict = distName;

        // Reset all layers style and highlight selected district
        if (this.hierCurrentLayer) {
            this.hierCurrentLayer.eachLayer(l => this.hierCurrentLayer.resetStyle(l));
        }
        if (districtLayer) {
            districtLayer.setStyle({
                fillColor: "#f39c12",
                color: "#ffffff",
                weight: 3,
                fillOpacity: 1.0
            });
            districtLayer.bringToFront();
            this.hierMap.fitBounds(districtLayer.getBounds(), { padding: [35, 35], maxZoom: 10 });
        }

        // Update UI
        document.getElementById("btn-back-to-state").style.display = "inline-flex";
        document.getElementById("bc-sep-dist").style.display = "inline";
        const bcDist = document.getElementById("bc-dist");
        bcDist.style.display = "inline";
        bcDist.textContent = distName;

        document.getElementById("map-pill-name").textContent = `${stateName} ❯ ${distName}`;

        // Find destinations in this district
        const normDist = this.normalizeName(distName);
        const aliases = (this.DISTRICT_ALIASES[normDist] || []).map(a => this.normalizeName(a));
        aliases.push(normDist);

        const matched = this.destinationsList.filter(d => {
            const dState = (d.state || "").toLowerCase().trim();
            const targetState = stateName.toLowerCase().trim();
            if (!dState.includes(targetState) && !targetState.includes(dState)) return false;

            const targetD = this.normalizeName(d.district || "");
            const placeNorm = this.normalizeName(d.place || "");

            // Direct check or alias check
            for (let a of aliases) {
                if (targetD === a || (a.length >= 4 && targetD.length >= 4 && (targetD.includes(a) || a.includes(targetD)))) {
                    return true;
                }
            }
            return false;
        });

        // Add pins on map for matched places
        if (this.hierPinsLayer) {
            this.hierPinsLayer.clearLayers();
        }

        const panel = document.getElementById("district-places-panel");
        const titleEl = document.getElementById("district-places-title");
        const countEl = document.getElementById("district-places-count");
        const cardsEl = document.getElementById("district-places-cards");

        panel.style.display = "block";
        titleEl.textContent = `📍 Tourist Destinations in ${distName} (${stateName})`;

        if (matched.length === 0) {
            countEl.textContent = "0 Destinations";
            cardsEl.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 24px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; text-align: center; color: #64748b;">
                    <i class="fa-solid fa-circle-exclamation" style="font-size: 24px; color: #94a3b8; margin-bottom: 8px;"></i>
                    <p style="font-size: 14px; font-weight: 600; color: #475569; margin: 0;">No tourist places are currently available in the dataset for this district.</p>
                    <span style="font-size: 12px; color: #94a3b8;">Try clicking a destination district such as <strong>Mysuru</strong>, <strong>Kodagu</strong>, or <strong>Ballari</strong>.</span>
                </div>
            `;
        } else {
            countEl.textContent = `${matched.length} Destination(s)`;
            let html = "";
            matched.forEach(m => {
                if (m.lat && m.lon) {
                    const marker = L.circleMarker([m.lat, m.lon], {
                        radius: 9,
                        fillColor: m.category_color || "#e11d48",
                        color: "#ffffff",
                        weight: 2,
                        fillOpacity: 1
                    }).addTo(this.hierPinsLayer);

                    marker.bindTooltip(`<strong>${m.place}</strong>`, { direction: 'top', permanent: true });
                }

                html += `
                    <div class="place-card" style="--place-accent: ${m.category_color || '#0284c7'};">
                        <h4>${m.place}</h4>
                        <div class="place-category">${m.category} • ${m.location_type || 'Landmark'}</div>
                        <div class="place-metrics">
                            <div><strong>Rating:</strong> ⭐ ${m.rating}/5.0</div>
                            <div><strong>Est. Cost:</strong> ₹${m.cost ? m.cost.toLocaleString() : 'N/A'}</div>
                            <div><strong>Avg Stay:</strong> ${m.stay} Days</div>
                            <div><strong>Best Time:</strong> ${m.best_time || 'All Year'}</div>
                        </div>
                        ${m.taluk ? `<div style="font-size: 11.5px; color: #475569; margin: 4px 0;"><strong>Taluk / Sub-District:</strong> ${m.taluk}</div>` : ''}
                        ${m.address ? `<div class="place-address">${m.address}</div>` : ''}
                        ${m.source_url ? `
                        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #f1f5f9; font-size: 11px;">
                            <a href="${m.source_url}" target="_blank" rel="noopener noreferrer" style="color: #0284c7; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                                <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 10px;"></i> Source: ${m.source_org || 'Official Government Portal'}
                            </a>
                        </div>` : ''}
                    </div>
                `;
            });
            cardsEl.innerHTML = html;
        }

        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
};
