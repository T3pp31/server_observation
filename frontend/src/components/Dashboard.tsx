import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Spinner } from 'react-bootstrap';
import { Device } from '../types';
import { deviceService } from '../services/api';
import DeviceDetailModal from './DeviceDetailModal';
import ScanModal from './ScanModal';

const Dashboard: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showScanModal, setShowScanModal] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    setLoading(true);
    try {
      const data = await deviceService.getDevices();
      setDevices(data);
    } catch (error) {
      console.error('デバイスの読み込みに失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNetworkScan = async () => {
    setLoading(true);
    try {
      await deviceService.scanNetwork();
      await loadDevices();
    } catch (error) {
      console.error('ネットワークスキャンに失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShowDetail = (ipAddress: string) => {
    setSelectedDevice(ipAddress);
    setShowDetailModal(true);
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      online: 'success',
      offline: 'danger',
      unknown: 'warning',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const stats = {
    total: devices.length,
    online: devices.filter(d => d.status === 'online').length,
    offline: devices.filter(d => d.status === 'offline').length,
    unknown: devices.filter(d => d.status === 'unknown').length,
  };

  return (
    <Container fluid className="p-4">
      <h1 className="mb-4">LAN監視ツール</h1>

      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>総機器数</Card.Title>
              <h2>{stats.total}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>オンライン</Card.Title>
              <h2 className="text-success">{stats.online}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>オフライン</Card.Title>
              <h2 className="text-danger">{stats.offline}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>不明</Card.Title>
              <h2 className="text-warning">{stats.unknown}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h4>機器一覧</h4>
            <div>
              <Button 
                variant="primary" 
                onClick={loadDevices} 
                disabled={loading}
                className="me-2"
              >
                更新
              </Button>
              <Button 
                variant="success" 
                onClick={handleNetworkScan}
                disabled={loading}
                className="me-2"
              >
                ネットワークスキャン
              </Button>
              <Button 
                variant="info" 
                onClick={() => setShowScanModal(true)}
                disabled={loading}
              >
                手動スキャン
              </Button>
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">読み込み中...</span>
              </Spinner>
            </div>
          ) : (
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>IPアドレス</th>
                  <th>MACアドレス</th>
                  <th>ホスト名</th>
                  <th>ベンダー</th>
                  <th>OS情報</th>
                  <th>ステータス</th>
                  <th>初回検知</th>
                  <th>最終確認</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td>{device.ip_address}</td>
                    <td>{device.mac_address || '-'}</td>
                    <td>{device.hostname || '-'}</td>
                    <td>{device.vendor || '-'}</td>
                    <td>{device.os_info || '-'}</td>
                    <td>{getStatusBadge(device.status)}</td>
                    <td>{new Date(device.first_detected).toLocaleString('ja-JP')}</td>
                    <td>{new Date(device.last_seen).toLocaleString('ja-JP')}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleShowDetail(device.ip_address)}
                      >
                        🔍
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {selectedDevice && (
        <DeviceDetailModal
          show={showDetailModal}
          onHide={() => setShowDetailModal(false)}
          ipAddress={selectedDevice}
        />
      )}

      <ScanModal
        show={showScanModal}
        onHide={() => setShowScanModal(false)}
        onScanComplete={loadDevices}
      />
    </Container>
  );
};

export default Dashboard;