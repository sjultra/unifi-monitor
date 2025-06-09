import { httpGet } from "@/utils";
import { Device, ListDevicesResponse } from "unifi-api";
import { UnifiEnvironment } from "@/config/environments";
import * as fs from 'fs';
import * as path from 'path';

const HOST = "https://api.ui.com"
const DEVICES_API = "/ea/devices"
const NETWORKS_API = "/ea/networks"

export interface DHCPReservation {
    mac: string;
    ip: string;
    hostname: string;
    description?: string;
}

interface Network {
    id: string;
    name: string;
    dhcpReservations: DHCPReservation[];
}

interface ListNetworksResponse {
    data: Network[];
    httpStatusCode: number;
    traceId: string;
    nextToken?: string;
}

export async function getHosts(env: UnifiEnvironment) {
    if (!env.apiKey) {
        console.log(`missing API key for environment: ${env.name}`);
        process.exit(1)
    }

    const data = await httpGet<ListDevicesResponse>(HOST, DEVICES_API, {
        'Accept': 'application/json',
        'X-API-KEY': env.apiKey,
    })
    console.log("HTTP response status:", data.httpStatusCode);

    const site = data.data.find(entry => entry.hostName === env.hostname)

    if (!site) {
        console.log(`Unifi host not found: '${env.hostname}'`);
        return
    }

    const devices = site.devices
    const online = devices.filter(device => device.status !== "offline")
    const offline = devices.filter(device => device.status === "offline")
    console.log("Devices found:", devices.length);
    console.log("Online devices:", online.length);
    console.log("Offline devices:", offline.length);

    if (devices.length === 0) {
        return
    }
    
    if (online.length === 0) {
        return
    }
    const summaries = online.map(extractDeviceSummary)
    const csv = formatToCSV(Object.keys(summaries[0]), summaries)
    console.log("CSV Dump:");
    console.log(csv);
}

interface DeviceSummary extends Pick<Device, 'name' | 'model' | 'shortname' | 'mac' | 'ip' | 'firmwareStatus'> { }

function extractDeviceSummary(device: Device): DeviceSummary {
    const { name, model, shortname, mac, ip, firmwareStatus } = device
    return {
        name,
        model,
        shortname,
        mac,
        ip,
        firmwareStatus
    }
}

function formatToCSV(columns: string[], rows: any[]): string {
    let csv = columns.join(",") + '\n'
    csv += rows.map(row => Object.values(row).join(",")).join('\n')
    return csv
}

export async function getDHCPReservations(env: UnifiEnvironment): Promise<DHCPReservation[]> {
    if (!env.apiKey) {
        console.log(`missing API key for environment: ${env.name}`);
        process.exit(1)
    }

    const data = await httpGet<ListNetworksResponse>(HOST, NETWORKS_API, {
        'Accept': 'application/json',
        'X-API-KEY': env.apiKey,
    })
    console.log("HTTP response status:", data.httpStatusCode);

    const site = data.data.find(entry => entry.name === env.hostname)

    if (!site) {
        console.log(`Unifi network not found: '${env.hostname}'`);
        return []
    }

    const reservations = site.dhcpReservations
    console.log("DHCP Reservations found:", reservations.length);

    // Export to JSON file
    const jsonOutput = JSON.stringify(reservations, null, 2);
    fs.writeFileSync(`dhcp-reservations-${env.name.toLowerCase()}.json`, jsonOutput);
    console.log(`DHCP reservations exported to dhcp-reservations-${env.name.toLowerCase()}.json`);

    // Update the dhcp.ts file
    updateDHCPConfigFile(env.name.toLowerCase(), reservations);

    return reservations;
}

function updateDHCPConfigFile(envName: string, reservations: DHCPReservation[]): void {
    const configPath = path.join(process.cwd(), 'src', 'config', 'dhcp.ts');
    const content = `import { DHCPReservation } from "@/clients/unifi";

export const dhcpReservations: { [key: string]: DHCPReservation[] } = {
    dev: ${envName === 'dev' ? JSON.stringify(reservations, null, 4) : '[]'},
    stage: ${envName === 'stage' ? JSON.stringify(reservations, null, 4) : '[]'},
    prod: ${envName === 'prod' ? JSON.stringify(reservations, null, 4) : '[]'}
};
`;

    fs.writeFileSync(configPath, content);
    console.log(`Updated dhcp.ts with ${envName} environment reservations`);
}

export function compareDHCPConfigurations(current: DHCPReservation[], desired: DHCPReservation[]): {
    toAdd: DHCPReservation[];
    toRemove: DHCPReservation[];
    unchanged: DHCPReservation[];
} {
    const toAdd = desired.filter(desiredRes => 
        !current.some(currentRes => currentRes.mac === desiredRes.mac)
    );
    
    const toRemove = current.filter(currentRes => 
        !desired.some(desiredRes => desiredRes.mac === currentRes.mac)
    );
    
    const unchanged = current.filter(currentRes => 
        desired.some(desiredRes => 
            desiredRes.mac === currentRes.mac &&
            desiredRes.ip === currentRes.ip &&
            desiredRes.hostname === currentRes.hostname &&
            desiredRes.description === currentRes.description
        )
    );

    return { toAdd, toRemove, unchanged };
}

export async function updateDHCPReservations(env: UnifiEnvironment, desiredReservations: DHCPReservation[]): Promise<void> {
    const currentReservations = await getDHCPReservations(env);
    const { toAdd, toRemove, unchanged } = compareDHCPConfigurations(currentReservations, desiredReservations);

    console.log("DHCP Changes:");
    console.log("To Add:", toAdd.length);
    console.log("To Remove:", toRemove.length);
    console.log("Unchanged:", unchanged.length);

    // TODO: Implement the actual API calls to update DHCP reservations
    // This would require additional API endpoints and implementation
    // For now, we'll just log the changes
    if (toAdd.length > 0 || toRemove.length > 0) {
        console.log("Changes detected - update functionality to be implemented");
    }
}