export interface Device {
  id: number;
  ip_address: string;
  mac_address?: string;
  hostname?: string;
  vendor?: string;
  os_info?: string;
  status: string;
  first_detected: string;
  last_seen: string;
}

export interface PortScan {
  id: number;
  device_ip: string;
  port: number;
  service?: string;
  service_name?: string;
  is_open: boolean;
  scan_time: string;
}

export interface HttpResponse {
  id: number;
  device_ip: string;
  url: string;
  status_code?: number;
  headers?: Record<string, string>;
  body_preview?: string;
  scan_time: string;
}

export interface DeviceDetail extends Device {
  port_scans: PortScan[];
  http_responses: HttpResponse[];
}