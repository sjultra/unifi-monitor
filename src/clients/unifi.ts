import { httpGet } from "@/utils";
import { Device, ListDevicesResponse } from "unifi-api";
import { UnifiEnvironment } from "@/config/environments";

const HOST = "https://api.ui.com"
const DEVICES_API = "/ea/devices"

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