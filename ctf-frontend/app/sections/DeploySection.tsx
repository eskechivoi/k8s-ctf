import React from 'react';
import { AlertTriangle, Loader2, RefreshCw, Play } from 'lucide-react';
import type { Dependency } from '@/lib/types';

interface DeploySectionProps {
    isLoading: boolean;
    dependencies: Dependency[];
    user: string;
    handleDeploy: (challengeName: string) => Promise<void>;
    fetchData: () => Promise<void>;
    isDeploying: boolean;
}

/**
 * Component to list the available challenges and to deploy them.
 */
const DeploySection: React.FC<DeploySectionProps> = ({ isLoading, dependencies, user, handleDeploy, fetchData, isDeploying }) => {
    if (isLoading) {
        return (
            <div className="p-8 text-center text-gray-500">
                <Loader2 className="w-8 h-8 mx-auto animate-spin" />
                <p className="mt-3">Loading available challenges...</p>
            </div>
        );
    }
    
    if (dependencies.length === 0) {
        return (
            <div className="p-8 text-center text-gray-500">
                <AlertTriangle className="w-8 h-8 mx-auto text-yellow-500" />
                <p className="mt-3">No challenges available to deploy. Upload one in the previous tab.</p>
                <button 
                    onClick={fetchData} 
                    className="mt-4 text-sm text-indigo-600 flex items-center mx-auto hover:text-indigo-800"
                >
                    <RefreshCw className="w-4 h-4 mr-1" /> Retry Load
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h3 className="text-xl font-bold text-gray-800 border-b pb-2 mb-4">Available Challenges ({dependencies.length})</h3>
            
            {dependencies.map((dep: Dependency) => (
                <div key={dep.name} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-xl shadow-sm">
                    <div>
                        <p className="text-lg font-semibold text-gray-900">{dep.name}</p>
                        <p className="text-sm text-gray-600">v{dep.version} | {dep.description}</p>
                    </div>
                    <button
                        onClick={() => handleDeploy(dep.name)}
                        disabled={!user || isDeploying}
                        className="flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-400 transition duration-150 shadow-md"
                    >
                        <Play className="w-4 h-4 mr-2" />
                        Deploy
                    </button>
                </div>
            ))}
            {!user && <p className="text-sm text-red-500 text-center pt-2">Enter your username above to enable deployment.</p>}
        </div>
    );
};

export default DeploySection;