import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Spinner, Dropdown, ButtonGroup, Form, InputGroup } from 'react-bootstrap';
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
  const [networkRange, setNetworkRange] = useState('192.168.1.0/24');

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

  const handleNetworkScan = async (networkRange?: string) => {
    setLoading(true);
    try {
      await deviceService.scanNetwork(networkRange);
      await loadDevices();
    } catch (error) {
      console.error('ネットワークスキャンに失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickScanOptions = [
    { label: 'デフォルト (192.168.1.0/24)', value: '192.168.1.0/24' },
    { label: '192.168.0.0/24', value: '192.168.0.0/24' },
    { label: '10.0.0.0/24', value: '10.0.0.0/24' },
    { label: '172.16.0.0/24', value: '172.16.0.0/24' },
    { label: '小範囲 (192.168.1.1-20)', value: '192.168.1.1-20' },
  ];

  const handleResetDevices = async () => {
    if (window.confirm('全てのデバイス情報を削除しますか？この操作は元に戻せません。')) {
      setLoading(true);
      try {
        await deviceService.resetDevices();
        await loadDevices();
      } catch (error) {
        console.error('リセットに失敗しました:', error);
      } finally {
        setLoading(false);
      }
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

      <Card className="mb-4">
        <Card.Header>
          <h5>ネットワークスキャン</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={8}>
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="ネットワーク範囲を入力 (例: 192.168.1.0/24, 10.0.0.1-20, 172.16.1.100)"
                  value={networkRange}
                  onChange={(e) => setNetworkRange(e.target.value)}
                  disabled={loading}
                />
                <Button 
                  variant="success" 
                  onClick={() => handleNetworkScan(networkRange)}
                  disabled={loading || !networkRange.trim()}
                >
                  {loading ? 'スキャン中...' : 'スキャン実行'}
                </Button>
              </InputGroup>
              <Form.Text className="text-muted">
                対応形式：CIDR記法（192.168.1.0/24）、範囲指定（192.168.1.1-20）、単一IP（192.168.1.100）
              </Form.Text>
            </Col>
            <Col md={4}>
              <div className="d-flex gap-2 flex-wrap">
                {quickScanOptions.map((option) => (
                  <Button 
                    key={option.value}
                    variant="outline-secondary"
                    size="sm"
                    onClick={() => setNetworkRange(option.value)}
                    disabled={loading}
                  >
                    {option.label.split(' ')[0]}
                  </Button>
                ))}
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>

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
                variant="info" 
                onClick={() => setShowScanModal(true)}
                disabled={loading}
                className="me-2"
              >
                詳細スキャン
              </Button>
              <Button 
                variant="danger" 
                onClick={handleResetDevices}
                disabled={loading}
              >
                リセット
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