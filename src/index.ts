import 'dotenv/config'
import * as UnifiClient from "@/clients/unifi"
import { dhcpReservations } from "@/config/dhcp"
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
        
        console.log("\nFetching DHCP reservations...");
        await UnifiClient.getDHCPReservations(env)
    } else if (mode === 'write') {
        console.log("Updating DHCP reservations from configuration...");
        await UnifiClient.updateDHCPReservations(env, dhcpReservations[envName] || [])
    } else {
        console.error("Invalid mode. Use 'read' or 'write'");
        process.exit(1)
    }
}

main()