import 'dotenv/config'

import * as UnifiClient from "@/clients/unifi"

async function main() {
    console.log("Fetching device information...");
    await UnifiClient.getHosts()
    
    console.log("\nFetching DHCP reservations...");
    await UnifiClient.getDHCPReservations()
}

main()