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
  const [customRange, setCustomRange] = useState('');
  const [useCustomRange, setUseCustomRange] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const commonNetworks = [
    { label: '192.168.1.0/24 (一般的な家庭用)', value: '192.168.1.0/24' },
    { label: '192.168.0.0/24 (一般的な家庭用)', value: '192.168.0.0/24' },
    { label: '10.0.0.0/24 (企業用)', value: '10.0.0.0/24' },
    { label: '172.16.0.0/24 (企業用)', value: '172.16.0.0/24' },
    { label: '192.168.1.1-20 (範囲指定)', value: '192.168.1.1-20' },
    { label: 'カスタム', value: 'custom' }
  ];

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

  const handleNetworkSelection = (value: string) => {
    if (value === 'custom') {
      setUseCustomRange(true);
      setNetworkRange('');
    } else {
      setUseCustomRange(false);
      setNetworkRange(value);
    }
  };

  const getCurrentRange = () => {
    return useCustomRange ? customRange : networkRange;
  };

  const handleScan = async () => {
    setScanning(true);
    setError(null);
    try {
      const currentRange = getCurrentRange();
      if (!currentRange.trim()) {
        setError('ネットワーク範囲を指定してください');
        return;
      }
      
      const normalizedRange = normalizeNetworkRange(currentRange);
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
            <Form.Select
              value={useCustomRange ? 'custom' : networkRange}
              onChange={(e) => handleNetworkSelection(e.target.value)}
              disabled={scanning}
              className="mb-2"
            >
              {commonNetworks.map((network) => (
                <option key={network.value} value={network.value}>
                  {network.label}
                </option>
              ))}
            </Form.Select>
            
            {useCustomRange && (
              <Form.Control
                type="text"
                placeholder="例: 192.168.1.0/24, 10.0.0.1-50, 172.16.1.100"
                value={customRange}
                onChange={(e) => setCustomRange(e.target.value)}
                disabled={scanning}
              />
            )}
            
            <Form.Text className="text-muted">
              対応形式：CIDR記法（192.168.1.0/24）、範囲指定（192.168.1.1-20）、単一IP（192.168.1.100）
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