declare namespace AdSystemSDK {
    interface AdOptions {
        age?: number;
        gender?: 'M' | 'F';
        location?: string;
        keywords?: string[];
        ab_test_group?: string;
    }

    function displayAd(containerId: string, options?: AdOptions): Promise<void>;
    function displayCarousel(containerId: string, carouselId: number): Promise<void>;
}
