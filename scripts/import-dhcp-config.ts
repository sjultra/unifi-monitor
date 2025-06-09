import * as fs from 'fs';
import * as path from 'path';
import { DHCPReservation } from '../src/clients/unifi';

const ENVIRONMENTS = ['dev', 'stage', 'prod'];

function readJsonFile(env: string): DHCPReservation[] {
    const filePath = path.join(process.cwd(), `dhcp-reservations-${env}.json`);
    try {
        if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf-8');
            return JSON.parse(content);
        }
        console.log(`No JSON file found for ${env} environment`);
        return [];
    } catch (error) {
        console.error(`Error reading ${env} JSON file:`, error);
        return [];
    }
}

function generateDHCPConfig(): void {
    const reservations: { [key: string]: DHCPReservation[] } = {};
    
    // Read all environment JSON files
    ENVIRONMENTS.forEach(env => {
        reservations[env] = readJsonFile(env);
    });

    // Generate the TypeScript file content
    const content = `import { DHCPReservation } from "@/clients/unifi";

export const dhcpReservations: { [key: string]: DHCPReservation[] } = ${JSON.stringify(reservations, null, 4)};
`;

    // Write to dhcp.ts
    const configPath = path.join(process.cwd(), 'src', 'config', 'dhcp.ts');
    fs.writeFileSync(configPath, content);
    console.log('Successfully imported DHCP configurations into dhcp.ts');
}

// Run the import
generateDHCPConfig(); 