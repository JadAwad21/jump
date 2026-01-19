import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import apiClient from '../../services/api';

export default function InvestigatorDashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedInvestigation, setSelectedInvestigation] = useState(null);
  const queryClient = useQueryClient();

  const { data: investigations } = useQuery({
    queryKey: ['investigations'],
    queryFn: async () => {
      const res = await apiClient.get('/blockchain/investigations/');
      return res.data.results || res.data;
    },
  });

  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const res = await apiClient.get('/blockchain/tags/');
      return res.data.results || res.data;
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Investigator Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button onClick={() => setShowCreateModal(true)}>Create Investigation</Button>
              <Button variant="secondary" onClick={() => {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = '/login';
              }}>Logout</Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card title="My Investigations">
          {investigations?.length > 0 ? (
            <div className="space-y-4">
              {investigations.map(inv => (
                <div key={inv.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{inv.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{inv.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        <span>Status: {inv.status}</span>
                        <span>Created: {new Date(inv.created_at).toLocaleDateString()}</span>
                        {inv.blockchain_tx_hash && (
                          <span className="text-green-600">✓ On Blockchain</span>
                        )}
                      </div>
                    </div>
                    <Button size="sm" onClick={() => {
                      setSelectedInvestigation(inv);
                      setShowUploadModal(true);
                    }}>Upload Evidence</Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No investigations yet. Create one to get started!</p>
          )}
        </Card>

        {showCreateModal && (
          <CreateInvestigationModal
            tags={tags}
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
              setShowCreateModal(false);
              queryClient.invalidateQueries(['investigations']);
            }}
          />
        )}

        {showUploadModal && (
          <UploadEvidenceModal
            investigation={selectedInvestigation}
            onClose={() => setShowUploadModal(false)}
            onSuccess={() => {
              setShowUploadModal(false);
              queryClient.invalidateQueries(['investigations']);
            }}
          />
        )}
      </main>
    </div>
  );
}

function CreateInvestigationModal({ tags, onClose, onSuccess }) {
  const [formData, setFormData] = useState({ title: '', description: '', tag_ids: [] });

  const createMutation = useMutation({
    mutationFn: async (data) => {
      await apiClient.post('/blockchain/investigations/', data);
    },
    onSuccess: () => {
      alert('Investigation created and recorded on blockchain!');
      onSuccess();
    },
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Create Investigation</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              value={formData.title}
              onChange={e => setFormData({...formData, title: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              rows="3"
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <select
              multiple
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              value={formData.tag_ids}
              onChange={e => setFormData({...formData, tag_ids: Array.from(e.target.selectedOptions, o => o.value)})}
            >
              {tags?.map(tag => (
                <option key={tag.id} value={tag.id}>{tag.name}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
          </div>
        </div>
        <div className="flex space-x-3 mt-6">
          <Button onClick={() => createMutation.mutate(formData)} disabled={!formData.title}>
            Create
          </Button>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  );
}

function UploadEvidenceModal({ investigation, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [anonymous, setAnonymous] = useState(false);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('investigation', investigation.id);
      formData.append('title', title);
      formData.append('description', description);
      formData.append('uploaded_anonymously', anonymous);
      
      await apiClient.post('/blockchain/evidence/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    onSuccess: () => {
      alert('Evidence uploaded to IPFS and recorded on blockchain!');
      onSuccess();
    },
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Upload Evidence</h2>
        <p className="text-sm text-gray-600 mb-4">Investigation: {investigation.title}</p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              rows="2"
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">File</label>
            <input
              type="file"
              className="w-full"
              onChange={e => setFile(e.target.files[0])}
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="anonymous"
              checked={anonymous}
              onChange={e => setAnonymous(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="anonymous" className="text-sm text-gray-700">
              Upload anonymously (GUID will be used)
            </label>
          </div>
        </div>
        <div className="flex space-x-3 mt-6">
          <Button onClick={() => uploadMutation.mutate()} disabled={!file || !title}>
            Upload
          </Button>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  );
}
