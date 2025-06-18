export interface UnifiEnvironment {
    name: string;
    hostname: string;
    apiKey: string;
    description?: string;
}

export const environments: { [key: string]: UnifiEnvironment } = {
    dev: {
        name: "Development",
        hostname: "Testing",
        apiKey: process.env.UNIFI_API_KEY_DEV || "",
        description: "Development environment for testing new configurations"
    },
    stage: {
        name: "Staging",
        hostname: "stage-testing",
        apiKey: process.env.UNIFI_API_KEY_STAGE || "",
        description: "Staging environment for pre-production testing"
    },
    prod: {
        name: "Production",
        hostname: "prod-testing",
        apiKey: process.env.UNIFI_API_KEY_PROD || "",
        description: "Production environment - handle with care"
    },
    lab: {
        name: "Lab",
        hostname: "lab-testing",
        apiKey: process.env.UNIFI_API_KEY_LAB || "",
        description: "Lab environment for experimental configurations"
    },
    demo: {
        name: "Demo",
        hostname: "demo-testing",
        apiKey: process.env.UNIFI_API_KEY_DEMO || "",
        description: "Demo environment for presentations and testing"
    }
}; 