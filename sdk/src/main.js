const API_BASE_URL = 'http://127.0.0.1:8000/ads/api/'; // Replace with your Django API base URL

const AdSystemSDK = {
    /**
     * Fetches and displays a single ad in the specified container.
     * @param {string} containerId The ID of the HTML element where the ad will be displayed.
     * @param {object} [options={}] Targeting and A/B testing options.
     * @param {number} [options.age] User's age.
     * @param {string} [options.gender] User's gender ('M' or 'F').
     * @param {string} [options.location] User's location (e.g., 'Spain').
     * @param {string[]} [options.keywords] Array of keywords describing user interests.
     * @param {string} [options.ab_test_group] A/B test group identifier.
     */
    displayAd: async (containerId, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`AdSystemSDK: Container with ID '${containerId}' not found.`);
            return;
        }

        const params = new URLSearchParams();
        for (const key in options) {
            if (Array.isArray(options[key])) {
                options[key].forEach(item => params.append(key, item));
            } else {
                params.append(key, options[key]);
            }
        }

        try {
            const response = await fetch(`${API_BASE_URL}ads/?${params.toString()}`);
            if (!response.ok) {
                if (response.status === 404) {
                    container.innerHTML = '<p>No ad available for this targeting.</p>';
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return;
            }
            const ad = await response.json();
            container.innerHTML = `
                <a href="${ad.target_url}" target="_blank" rel="noopener noreferrer">
                    <img src="${ad.image}" alt="${ad.name}" style="max-width: 100%; height: auto;">
                </a>
                <p>${ad.name}</p>
            `;
        } catch (error) {
            console.error('AdSystemSDK: Error fetching ad:', error);
            container.innerHTML = '<p>Failed to load ad.</p>';
        }
    },

    /**
     * Fetches and displays a carousel of ads in the specified container.
     * @param {string} containerId The ID of the HTML element where the carousel will be displayed.
     * @param {number} carouselId The ID of the carousel to display.
     */
    displayCarousel: async (containerId, carouselId) => {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`AdSystemSDK: Container with ID '${containerId}' not found.`);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}carousels/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const carousels = await response.json();
            const carousel = carousels.find(c => c.id === carouselId);

            if (!carousel) {
                container.innerHTML = '<p>Carousel not found or not active.</p>';
                return;
            }

            if (!carousel.ads || carousel.ads.length === 0) {
                container.innerHTML = '<p>No ads in this carousel.</p>';
                return;
            }

            // Simple carousel implementation (can be enhanced with JS for sliding)
            let carouselHtml = `
                <h3 class="text-xl font-semibold mb-2">${carousel.name}</h3>
                <div class="flex overflow-x-auto space-x-4 p-2">
            `;
            carousel.ads.forEach(ad => {
                carouselHtml += `
                    <div class="flex-none w-64">
                        <a href="${ad.target_url}" target="_blank" rel="noopener noreferrer">
                            <img src="${ad.image}" alt="${ad.name}" class="w-full h-32 object-cover">
                        </a>
                        <p class="text-sm mt-1">${ad.name}</p>
                    </div>
                `;
            });
            carouselHtml += `</div>`;
            container.innerHTML = carouselHtml;

        } catch (error) {
            console.error('AdSystemSDK: Error fetching carousel:', error);
            container.innerHTML = '<p>Failed to load carousel.</p>';
        }
    }
};

window.AdSystemSDK = AdSystemSDK;
