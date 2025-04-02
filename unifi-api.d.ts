/// <reference types="node" />

// unifi-api.d.ts

declare module 'unifi-api' {
    export interface UIDB {
      guid: string;
      id: string;
      images: {
        default: string;
        nopadding: string;
        topology: string;
      };
    }
  
    export interface Device {
      adoptionTime?: string | null;
      firmwareStatus: string;
      id: string;
      ip: string;
      isConsole: boolean;
      isManaged: boolean;
      mac: string;
      model: string;
      name: string;
      note?: string | null;
      productLine: string;
      shortname: string;
      startupTime: string;
      status: string;
      uidb: UIDB;
      updateAvailable?: string | null;
      version: string;
    }
  
    export interface DeviceData {
      devices: Device[];
      hostId: string;
      hostName: string;
      updatedAt: string;
    }
  
    export interface ListDevicesResponse {
      data: DeviceData[];
      httpStatusCode: number;
      traceId: string;
      nextToken?: string;
    }
  }