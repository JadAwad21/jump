import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Card from '../common/Card';
import Button from '../common/Button';
import Badge from '../common/Badge';
import apiClient from '../../services/api';
import { formatDate } from '../../utils/formatters';

export default function CertificateManagement() {
  const [selectedUser, setSelectedUser] = useState('');

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await apiClient.get('/users/users/');
      return response.data.results || response.data;
    },
  });

  const { data: certificates, isLoading, refetch } = useQuery({
    queryKey: ['certificates'],
    queryFn: async () => {
      const response = await apiClient.get('/pki/certificates/');
      return response.data.results || response.data;
    },
  });

  const handleIssueCert = async () => {
    try {
      const body = selectedUser ? { username: selectedUser } : {};
      await apiClient.post("/pki/certificates/issue/", body);
      alert(`Certificate issued for ${selectedUser}!`);
      refetch();
      setSelectedUser('');
    } catch (err) {
      alert(err.response?.data?.error || "Failed");
    }
  };

  const handleDownload = async (certId, username) => {
    try {
      const response = await apiClient.get(`/pki/certificates/${certId}/download/`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${username}.p12`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Download failed: " + (err.response?.data?.error || err.message));
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <Card title="Certificate Management">
      <div className="mb-4 flex gap-3">
        <select 
          value={selectedUser} 
          onChange={(e) => setSelectedUser(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">Select User</option>
          {users?.map(u => (
            <option key={u.id} value={u.username}>{u.username} ({u.name})</option>
          ))}
        </select>
        <Button onClick={handleIssueCert} disabled={!selectedUser}>
          Issue Certificate
        </Button>
      </div>

      {certificates?.length > 0 ? (
        <div className="space-y-2">
          {certificates.map((cert) => (
            <div key={cert.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
              <div>
                <div className="font-medium">{cert.user_display}</div>
                <div className="text-sm text-gray-500">Serial: {cert.serial_number}</div>
                <div className="text-xs text-gray-400">Expires: {formatDate(cert.not_after)}</div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant={cert.revoked ? 'danger' : 'success'}>
                  {cert.revoked ? 'Revoked' : 'Active'}
                </Badge>
                {!cert.revoked && (
                  <Button variant="primary" size="sm"
                    onClick={() => handleDownload(cert.id, cert.user_display)}>
                    Download
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center py-8 text-gray-600">No certificates</p>
      )}
    </Card>
  );
}
