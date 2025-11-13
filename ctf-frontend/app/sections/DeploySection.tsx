import React from 'react';
import { List, Loader, RefreshCw, Send } from 'lucide-react';
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
const DeploySection: React.FC<DeploySectionProps> = ({ isLoading, dependencies, user, handleDeploy, fetchData, isDeploying }) => (
    <>
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">2. Available Challenges</h2>
            <button 
                onClick={fetchData} 
                disabled={isLoading}
                className={`p-2 rounded-full text-gray-500 hover:text-indigo-600 transition-colors ${isLoading ? 'animate-spin' : ''}`}
                title="Reload list"
            >
                <RefreshCw className="w-5 h-5" />
            </button>
        </div>
        
        {isLoading ? (
            <div className="text-center py-8 text-indigo-500">
                <Loader className="w-8 h-8 mx-auto animate-spin" />
                <p className="mt-2">Loading challenges...</p>
            </div>
        ) : dependencies.length === 0 ? (
            <div className="text-center py-8 text-gray-500 border border-dashed p-4 rounded-lg">
                <List className="w-6 h-6 mx-auto mb-2" />
                <p>There are no challenges uploaded. Use the 'Upload Challenge' tab.</p>
            </div>
        ) : (
            <ul className="space-y-3 max-h-96 overflow-y-auto pr-2">
                {dependencies.map((dep) => (
                    <li 
                        key={dep.name} 
                        className="flex justify-between items-center p-4 bg-gray-50 rounded-xl shadow-sm border border-gray-200"
                    >
                        <div>
                            <p className="font-semibold text-gray-800">{dep.name}</p>
                            <p className="text-sm text-gray-500">Version: {dep.version} | Updated: {dep.lastUpdated}</p>
                        </div>
                        <button
                            onClick={() => handleDeploy(dep.name)}
                            disabled={!user || isDeploying}
                            className={`flex items-center px-4 py-2 text-sm font-medium rounded-full transition duration-300 ${
                                !user || isDeploying
                                    ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                                    : 'bg-indigo-500 text-white hover:bg-indigo-600 shadow-lg'
                            }`}
                        >
                            <Send className="w-4 h-4 mr-1" />
                            Deploy
                        </button>
                    </li>
                ))}
            </ul>
        )}
    </>
);

export default DeploySection;