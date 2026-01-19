import { Link } from 'react-router-dom';

export default function Navbar({ onLogout }) {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/admin-dashboard" className="text-xl font-semibold text-gray-900">
              TruefyPJS Admin
            </Link>
          </div>
          <div className="flex items-center">
            <button
              onClick={onLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
