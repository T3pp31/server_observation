import React, { useState, useEffect } from 'react';
import { Modal, Button, Table, Alert, Spinner, Nav, Tab } from 'react-bootstrap';
import { DeviceDetail, PortScan, HttpResponse } from '../types';
import { deviceService } from '../services/api';

interface DeviceDetailModalProps {
  show: boolean;
  onHide: () => void;
  ipAddress: string;
}

const DeviceDetailModal: React.FC<DeviceDetailModalProps> = ({ show, onHide, ipAddress }) => {
  const [deviceDetail, setDeviceDetail] = useState<DeviceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (show && ipAddress) {
      loadDeviceDetail();
    }
  }, [show, ipAddress]);

  const loadDeviceDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await deviceService.getDeviceDetail(ipAddress);
      setDeviceDetail(data);
    } catch (error) {
      setError('デバイス詳細の読み込みに失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handlePortScan = async () => {
    setScanning(true);
    try {
      await deviceService.scanPorts(ipAddress);
      await loadDeviceDetail();
    } catch (error) {
      setError('ポートスキャンに失敗しました');
      console.error(error);
    } finally {
      setScanning(false);
    }
  };

  const renderPortScans = (portScans: PortScan[]) => {
    if (portScans.length === 0) {
      return <Alert variant="info">ポートスキャン結果がありません</Alert>;
    }

    return (
      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th>ポート番号</th>
            <th>サービス種別</th>
            <th>サービス名</th>
            <th>状態</th>
            <th>スキャン日時</th>
          </tr>
        </thead>
        <tbody>
          {portScans.map((scan) => (
            <tr key={scan.id}>
              <td>{scan.port}</td>
              <td>{scan.service || '-'}</td>
              <td>{scan.service_name || '-'}</td>
              <td>{scan.is_open ? '開放' : '閉鎖'}</td>
              <td>{new Date(scan.scan_time).toLocaleString('ja-JP')}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    );
  };

  const renderHttpResponses = (httpResponses: HttpResponse[]) => {
    if (httpResponses.length === 0) {
      return <Alert variant="info">HTTPレスポンス情報がありません</Alert>;
    }

    return httpResponses.map((response) => (
      <div key={response.id} className="mb-4 border rounded p-3">
        <h6>
          <a href={response.url} target="_blank" rel="noopener noreferrer">
            {response.url}
          </a>
        </h6>
        <p>ステータスコード: {response.status_code || 'N/A'}</p>
        
        {response.headers && (
          <>
            <h6>レスポンスヘッダー:</h6>
            <Table striped bordered hover size="sm">
              <tbody>
                {Object.entries(response.headers).map(([key, value]) => (
                  <tr key={key}>
                    <td style={{ width: '30%' }}>{key}</td>
                    <td>{value}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </>
        )}
        
        {response.body_preview && (
          <>
            <h6>レスポンスボディ（プレビュー）:</h6>
            <pre className="bg-light p-2" style={{ maxHeight: '200px', overflow: 'auto' }}>
              {response.body_preview}
            </pre>
          </>
        )}
        
        <small className="text-muted">
          スキャン日時: {new Date(response.scan_time).toLocaleString('ja-JP')}
        </small>
      </div>
    ));
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>デバイス詳細 - {ipAddress}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">読み込み中...</span>
            </Spinner>
          </div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : deviceDetail ? (
          <Tab.Container defaultActiveKey="port-scans">
            <Nav variant="tabs" className="mb-3">
              <Nav.Item>
                <Nav.Link eventKey="port-scans">ポートスキャン結果</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="http-responses">HTTPレスポンス</Nav.Link>
              </Nav.Item>
            </Nav>
            <Tab.Content>
              <Tab.Pane eventKey="port-scans">
                <div className="mb-3">
                  <Button
                    variant="primary"
                    onClick={handlePortScan}
                    disabled={scanning}
                  >
                    {scanning ? '全ポートスキャン中... (1-65535)' : '全ポートスキャン実行 (1-65535)'}
                  </Button>
                  {scanning && (
                    <div className="mt-2">
                      <small className="text-muted">
                        全ポート（65535個）をスキャンしています。完了まで数分かかる場合があります。
                      </small>
                    </div>
                  )}
                </div>
                {renderPortScans(deviceDetail.port_scans)}
              </Tab.Pane>
              <Tab.Pane eventKey="http-responses">
                {renderHttpResponses(deviceDetail.http_responses)}
              </Tab.Pane>
            </Tab.Content>
          </Tab.Container>
        ) : null}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          閉じる
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeviceDetailModal;