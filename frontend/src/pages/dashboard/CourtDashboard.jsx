import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import apiClient from '../../services/api';

export default function CourtDashboard() {
  const [guid, setGuid] = useState('');
  const [resolvedData, setResolvedData] = useState(null);

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

  const resolveGuid = async () => {
    try {
      const res = await apiClient.get(`/blockchain/guid-resolver/resolve/?guid=${guid}`);
      setResolvedData(res.data);
      alert(`Resolved: ${res.data.investigator_name} (${res.data.investigator})`);
    } catch (err) {
      alert('GUID not found or invalid');
      setResolvedData(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Court Dashboard</h1>
              <span className="ml-4 px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">GUID Resolution</span>
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
        <div className="mb-6">
          <Card title="Resolve Anonymous GUID">
            <div className="flex space-x-3">
              <input
                type="text"
                placeholder="Enter GUID (e.g., 550e8400-e29b-41d4-a716-446655440000)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                value={guid}
                onChange={e => setGuid(e.target.value)}
              />
              <Button onClick={resolveGuid} disabled={!guid}>Resolve</Button>
            </div>
            {resolvedData && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded">
                <p className="text-sm"><strong>Investigator:</strong> {resolvedData.investigator_name}</p>
                <p className="text-sm"><strong>Username:</strong> {resolvedData.investigator}</p>
              </div>
            )}
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="All Investigations">
            {investigations?.map(inv => (
              <div key={inv.id} className="border border-gray-200 rounded p-3 mb-3">
                <h3 className="font-medium">{inv.title}</h3>
                <p className="text-sm text-gray-600">{inv.description}</p>
              </div>
            ))}
          </Card>

          <Card title="Evidence (with Real Names)">
            {evidence?.map(ev => (
              <div key={ev.id} className="border border-gray-200 rounded p-3 mb-3">
                <h3 className="font-medium">{ev.title}</h3>
                <p className="text-xs text-gray-600">Uploaded by: {ev.uploaded_by_display}</p>
              </div>
            ))}
          </Card>
        </div>
      </main>
    </div>
  );
}
