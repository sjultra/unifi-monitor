import { DHCPReservation } from "@/clients/unifi";

export const dhcpReservations: { [key: string]: DHCPReservation[] } = {
    dev: [
        // {
        //     mac: "00:11:22:33:44:55",
        //     ip: "192.168.1.100",
        //     hostname: "dev-server-1",
        //     description: "Development server"
        // },
        // {
        //     mac: "00:11:22:33:44:56",
        //     ip: "192.168.1.101",
        //     hostname: "dev-workstation-1",
        //     description: "Developer workstation"
        // }
    ],
    stage: [
        // {
        //     mac: "00:11:22:33:44:57",
        //     ip: "192.168.2.100",
        //     hostname: "stage-server-1",
        //     description: "Staging server"
        // },
        // {
        //     mac: "00:11:22:33:44:58",
        //     ip: "192.168.2.101",
        //     hostname: "stage-db-1",
        //     description: "Staging database server"
        // }
    ],
    prod: [
        // {
        //     mac: "00:11:22:33:44:59",
        //     ip: "192.168.3.100",
        //     hostname: "prod-web-1",
        //     description: "Production web server"
        // },
        // {
        //     mac: "00:11:22:33:44:60",
        //     ip: "192.168.3.101",
        //     hostname: "prod-db-1",
        //     description: "Production database server"
        // },
        // {
        //     mac: "00:11:22:33:44:61",
        //     ip: "192.168.3.102",
        //     hostname: "prod-cache-1",
        //     description: "Production cache server"
        // }
    ]
}; 