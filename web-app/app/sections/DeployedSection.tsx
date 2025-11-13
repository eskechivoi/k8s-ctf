import React from 'react';
import { Loader, RefreshCw, Server } from 'lucide-react';
import DeploymentItem from '../components/DeploymentItem';
import type { Deployment } from '@/lib/types';

interface DeployedSectionProps {
    isLoading: boolean;
    deployments: Deployment[];
    fetchData: () => Promise<void>;
}

/**
 * Component to list all the active Helm releases.
 */
const DeployedSection: React.FC<DeployedSectionProps> = ({ isLoading, deployments, fetchData }) => (
    <>
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">3. Deployed Challenges</h2>
            <button 
                onClick={fetchData} 
                disabled={isLoading}
                className={`p-2 rounded-full text-gray-500 hover:text-indigo-600 transition-colors ${isLoading ? 'animate-spin' : ''}`}
                title="Reload Deployments"
            >
                <RefreshCw className="w-5 h-5" />
            </button>
        </div>
        
        {isLoading ? (
            <div className="text-center py-8 text-indigo-500">
                <Loader className="w-8 h-8 mx-auto animate-spin" />
                <p className="mt-2">Loading deployments...</p>
            </div>
        ) : deployments.length === 0 ? (
            <div className="text-center py-8 text-gray-500 border border-dashed p-4 rounded-lg">
                <Server className="w-6 h-6 mx-auto mb-2" />
                <p>There are no active Helm deployments (Challenges).</p>
            </div>
        ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                {deployments.map((dep) => (
                    <DeploymentItem key={dep.release_name} deployment={dep} />
                ))}
            </div>
        )}
    </>
);

export default DeployedSection;