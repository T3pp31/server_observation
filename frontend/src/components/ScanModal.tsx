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

  const normalizeNetworkRange = (input: string): string => {
    const trimmed = input.trim();
    
    // すでにCIDR形式の場合はそのまま返す
    if (trimmed.includes('/')) {
      return trimmed;
    }
    
    // 単一IPアドレスの場合は/32を追加
    // 簡易的なIPv4チェック
    const ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipv4Pattern.test(trimmed)) {
      return `${trimmed}/32`;
    }
    
    // それ以外はそのまま返す（バックエンドでバリデーション）
    return trimmed;
  };

  const handleScan = async () => {
    setScanning(true);
    setError(null);
    try {
      const normalizedRange = normalizeNetworkRange(networkRange);
      console.log('Scanning network range:', normalizedRange);
      
      const response = await deviceService.scanNetwork(normalizedRange);
      console.log('Scan response:', response);
      
      onScanComplete();
      onHide();
    } catch (error: any) {
      console.error('Scan error:', error);
      
      // エラーメッセージを詳細化
      if (error.response) {
        // APIからのエラーレスポンス
        const errorMessage = error.response.data?.detail || error.response.data?.message || 'ネットワークスキャンに失敗しました';
        setError(`エラー: ${errorMessage}`);
      } else if (error.request) {
        // リクエストは送信されたがレスポンスがない
        setError('サーバーに接続できません');
      } else {
        // その他のエラー
        setError('ネットワークスキャンに失敗しました');
      }
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
              CIDR形式（例: 192.168.1.0/24）または単一IPアドレス（例: 192.168.1.100）を入力してください
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