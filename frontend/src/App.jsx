import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import MFASetup from './pages/MFASetup';
import MFAChallenge from './pages/MFAChallenge';
import AdminDashboard from './pages/admin/AdminDashboard';
import InvestigatorDashboard from './pages/dashboard/InvestigatorDashboard';
import AuditorDashboard from './pages/dashboard/AuditorDashboard';
import CourtDashboard from './pages/dashboard/CourtDashboard';
import NotFound from './pages/NotFound';

const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>
);

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, loading, mfaStatus, isAdmin } = useAuth();

  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;

  // If MFA is not required or already verified, allow access
  if (!mfaStatus?.mfa_required || mfaStatus?.mfa_verified) {
    if (requireAdmin && !isAdmin()) return <Navigate to="/dashboard" replace />;
    return children;
  }

  // MFA is required but not verified
  if (mfaStatus?.needs_setup) return <Navigate to="/setup-mfa" replace />;
  return <Navigate to="/mfa-challenge" replace />;
};

function DashboardRouter() {
  const { user, isAdmin } = useAuth();
  
  if (isAdmin()) {
    return <Navigate to="/admin-dashboard" replace />;
  }
  
  const roleBindings = user?.role_bindings || [];
  const hasRole = (roleName) => roleBindings.some(rb => rb.role?.name === roleName);
  
  if (hasRole('Investigator')) {
    return <InvestigatorDashboard />;
  } else if (hasRole('Auditor')) {
    return <AuditorDashboard />;
  } else if (hasRole('Court')) {
    return <CourtDashboard />;
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">No Dashboard Available</h2>
        <p className="text-gray-600 mt-2">You don't have a blockchain role assigned.</p>
      </div>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/setup-mfa" element={<MFASetup />} />
      <Route path="/mfa-challenge" element={<MFAChallenge />} />
      
      <Route path="/admin-dashboard/*" element={<ProtectedRoute requireAdmin><AdminDashboard /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardRouter /></ProtectedRoute>} />
      
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
