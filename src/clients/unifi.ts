import { httpGet } from "@/utils";
import { Device, ListDevicesResponse } from "unifi-api";

const TARGET_HOSTNAME = "Testing"
const HOST = "https://api.ui.com"
const DEVICES_API = "/ea/devices"

const UNIFI_API_KEY = process.env.UNIFI_API_KEY as string
if (!UNIFI_API_KEY) {
    console.log("missing environment variable 'UNIFI_API_KEY'");
    process.exit(1)
}

export async function getHosts() {
    const data = await httpGet<ListDevicesResponse>(HOST, DEVICES_API, {
        'Accept': 'application/json',
        'X-API-KEY': UNIFI_API_KEY,
    })
    console.log("HTTP response status:", data.httpStatusCode);

    const site = data.data.find(entry => entry.hostName === TARGET_HOSTNAME)

    if (!site) {
        console.log(`Unifi host not found: '${TARGET_HOSTNAME}'`);
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