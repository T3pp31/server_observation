import React, { useState } from 'react';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import { deviceService } from '../services/api';

interface ScanModalProps {
  show: boolean;
  onHide: () => void;
  onScanComplete: () => void;
}

const ScanModal: React.FC<ScanModalProps> = ({ show, onHide, onScanComplete }) => {
  const [networkRange, setNetworkRange] = useState('192.168.1.0/24');
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setScanning(true);
    setError(null);
    try {
      await deviceService.scanNetwork(networkRange);
      onScanComplete();
      onHide();
    } catch (error) {
      setError('ネットワークスキャンに失敗しました');
      console.error(error);
    } finally {
      setScanning(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>手動ネットワークスキャン</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>ネットワーク範囲</Form.Label>
            <Form.Control
              type="text"
              placeholder="例: 192.168.1.0/24"
              value={networkRange}
              onChange={(e) => setNetworkRange(e.target.value)}
              disabled={scanning}
            />
            <Form.Text className="text-muted">
              CIDR形式でネットワーク範囲を指定してください
            </Form.Text>
          </Form.Group>
        </Form>
        {error && <Alert variant="danger">{error}</Alert>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={scanning}>
          キャンセル
        </Button>
        <Button variant="primary" onClick={handleScan} disabled={scanning}>
          {scanning ? 'スキャン中...' : 'スキャン開始'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ScanModal;