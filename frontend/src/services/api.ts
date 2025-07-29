import axios from 'axios';
import { Device, DeviceDetail } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://10.10.15.212:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const deviceService = {
  // 全デバイスを取得
  getDevices: async (): Promise<Device[]> => {
    const response = await api.get('/api/devices');
    return response.data;
  },

  // デバイスの詳細を取得
  getDeviceDetail: async (ipAddress: string): Promise<DeviceDetail> => {
    const response = await api.get(`/api/devices/${ipAddress}`);
    return response.data;
  },

  // ネットワークスキャンを実行
  scanNetwork: async (networkRange?: string) => {
    const response = await api.post('/api/scan/network', {
      network_range: networkRange,
    });
    return response.data;
  },

  // ポートスキャンを実行
  scanPorts: async (ipAddress: string) => {
    const response = await api.post('/api/scan/ports', {
      ip_address: ipAddress,
    });
    return response.data;
  },

  // デバイス情報を更新
  updateDevice: async (ipAddress: string, data: Partial<Device>) => {
    const response = await api.put(`/api/devices/${ipAddress}`, data);
    return response.data;
  },
};
