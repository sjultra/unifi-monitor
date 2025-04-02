import 'dotenv/config'

import * as UnifiClient from "@/clients/unifi"

async function main() {
    await UnifiClient.getHosts()
}

main()