import React from 'react';
import { AlertTriangle, CheckCircle, Loader2, Trash2, Clipboard } from 'lucide-react';
import type { Deployment } from '@/lib/types';
import { fetchApi } from '@/lib/fetchApi';

const DeploymentItem: React.FC<{ deployment: Deployment, fetchData: () => Promise<void> }> = ({ deployment, fetchData }) => {
    
    const handleCleanup = async (releaseName: string) => {
        try {
            console.log(`Simulating cleanup for ${releaseName}...`); 
            
            await fetchApi<{ message: string }, { release_name: string }>('/api/deployment', 'DELETE', { release_name: releaseName });

            alert(`Cleanup successful for ${releaseName}.`);
            await fetchData();
            
        } catch (error) {
             alert(`Error during cleanup for ${releaseName}. See console for details.`);
             console.error('Cleanup Error:', error);
        }
    };
    
    const handleCopy = (text: string) => {
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('URL copied to clipboard!');
    };

    const statusMap = {
        'deployed': { color: 'text-green-600 bg-green-100', icon: CheckCircle, label: 'Deployed' },
        'pending-upgrade': { color: 'text-yellow-600 bg-yellow-100', icon: Loader2, label: 'Updating...' },
        'failed': { color: 'text-red-600 bg-red-100', icon: AlertTriangle, label: 'Failed' },
        'error': { color: 'text-red-600 bg-red-100', icon: AlertTriangle, label: 'API Error' },
    };

    const status = statusMap[deployment.status] || statusMap.failed;
    const Icon = status.icon;

    return (
        <div className="p-4 bg-white border border-gray-200 rounded-xl shadow-md transition-shadow hover:shadow-lg flex flex-col sm:flex-row justify-between sm:items-center space-y-3 sm:space-y-0">
            <div className="flex-1 min-w-0">
                <p className="text-lg font-bold text-gray-900 truncate" title={deployment.release_name}>
                    {deployment.release_name}
                </p>
                <div className="flex items-center space-x-2 mt-1">
                    <span className={`flex items-center text-xs font-medium px-2.5 py-0.5 rounded-full ${status.color}`}>
                        <Icon className={`w-3 h-3 mr-1 ${deployment.status === 'pending-upgrade' ? 'animate-spin' : ''}`} />
                        {status.label}
                    </span>
                    <span className="text-sm text-gray-500 italic">Chart: {deployment.chart}</span>
                </div>
                {deployment.service_url && (
                    <div className="mt-2 flex items-center space-x-2 text-sm text-blue-700">
                        <a 
                            href={deployment.service_url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="truncate hover:underline"
                            title={deployment.service_url}
                        >
                            {deployment.service_url}
                        </a>
                        <button 
                            onClick={() => handleCopy(deployment.service_url || '')}
                            className="p-1 rounded-full hover:bg-gray-200"
                            title="Copy URL"
                        >
                            <Clipboard className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </div>
            
            <div className="flex space-x-2">
                <button
                    onClick={() => handleCleanup(deployment.release_name)}
                    disabled={deployment.status === 'pending-upgrade'}
                    className="flex items-center px-4 py-2 text-sm font-medium rounded-lg text-red-600 bg-white border border-red-300 hover:bg-red-50 disabled:bg-gray-100 transition duration-150 shadow-sm"
                >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Cleanup
                </button>
            </div>
        </div>
    );
};

export default DeploymentItem;