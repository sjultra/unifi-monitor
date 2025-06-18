import 'dotenv/config'
import * as UnifiClient from "@/clients/unifi"
import { environments } from "@/config/environments"

async function main() {
    const mode = process.argv[2] || 'read'
    const envName = process.argv[3] || 'dev'
    const env = environments[envName]

    if (!env) {
        console.error(`Invalid environment: ${envName}. Available environments: ${Object.keys(environments).join(', ')}`);
        process.exit(1)
    }

    console.log(`Running in ${env.name} environment...`);

    if (mode === 'read') {
        console.log("Fetching device information...");
        await UnifiClient.getHosts(env)
    } else {
        console.error("Invalid mode. Only 'read' is supported after DHCP removal.");
        process.exit(1)
    }
}

main();