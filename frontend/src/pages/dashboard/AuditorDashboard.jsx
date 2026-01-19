import { useQuery } from '@tanstack/react-query';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import apiClient from '../../services/api';

export default function AuditorDashboard() {
  const { data: investigations } = useQuery({
    queryKey: ['investigations'],
    queryFn: async () => {
      const res = await apiClient.get('/blockchain/investigations/');
      return res.data.results || res.data;
    },
  });

  const { data: evidence } = useQuery({
    queryKey: ['evidence'],
    queryFn: async () => {
      const res = await apiClient.get('/blockchain/evidence/');
      return res.data.results || res.data;
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Auditor Dashboard</h1>
              <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">Read Only</span>
            </div>
            <Button variant="secondary" onClick={() => {
              localStorage.clear();
              sessionStorage.clear();
              window.location.href = '/login';
            }}>Logout</Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="All Investigations">
            {investigations?.length > 0 ? (
              <div className="space-y-3">
                {investigations.map(inv => (
                  <div key={inv.id} className="border border-gray-200 rounded p-3">
                    <h3 className="font-medium text-gray-900">{inv.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{inv.description}</p>
                    <div className="flex items-center space-x-3 mt-2 text-xs text-gray-500">
                      <span>By: {inv.created_by_name}</span>
                      <span>Status: {inv.status}</span>
                      {inv.blockchain_tx_hash && <span className="text-green-600">✓ Blockchain</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No investigations found</p>
            )}
          </Card>

          <Card title="All Evidence">
            {evidence?.length > 0 ? (
              <div className="space-y-3">
                {evidence.map(ev => (
                  <div key={ev.id} className="border border-gray-200 rounded p-3">
                    <h3 className="font-medium text-gray-900">{ev.title}</h3>
                    <div className="text-xs text-gray-500 mt-2 space-y-1">
                      <div>File: {ev.file_name}</div>
                      <div>Uploaded by: {ev.uploaded_by_display}</div>
                      <div>IPFS: {ev.ipfs_hash?.substring(0, 20)}...</div>
                      {ev.blockchain_tx_hash && <div className="text-green-600">✓ Blockchain verified</div>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No evidence found</p>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
