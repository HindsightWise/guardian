
import { GlossopetraeKernel } from '../core/glossopetrae_kernel.mjs';
import https from 'https';

class CFTCSkill extends GlossopetraeKernel {
    constructor() {
        super('Finance/CFTC');
    }

    async fetchCOT(ticker) {
        this.log(`Fetching COT data for ${ticker}...`);

        // Mocking External API call for efficiency demo (or using real logic if available)
        // In the original script, it fetched from a public endpoint.
        // For the refactor, we maintain the logic but wrap it.

        const url = `https://publicreporting.cftc.gov/sda/soda/resource/jun7-fc8e.json?$limit=1&$order=report_date_as_yyyy_mm_dd%20DESC`;

        return new Promise((resolve, reject) => {
            https.get(url, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const json = JSON.parse(data);
                        this.log(`Data received. Records: ${json.length}`);
                        console.log(JSON.stringify(json, null, 2));
                        resolve(json);
                    } catch (e) {
                        this.log(`Parse error: ${e.message}`, 'ERROR');
                        reject(e);
                    }
                });
            }).on('error', (e) => {
                this.log(`Network error: ${e.message}`, 'ERROR');
                reject(e);
            });
        });
    }
}

const ticker = process.argv[2] || 'BTC';
new CFTCSkill().fetchCOT(ticker);
