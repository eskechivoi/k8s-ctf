'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Server, Upload, Send, List } from 'lucide-react';

import TabButton from './components/TabButton';
import MessageBox from './components/MessageBox';
import UploadSection from './sections/UploadSection';
import DeploySection from './sections/DeploySection';
import DeployedSection from './sections/DeployedSection';

import { mockFetch } from '@/lib/mockApi'; 
import type { Dependency, Deployment, Message } from '@/lib/types';

/**
 * Main component (Page) that manages global state of the application.
 */
const Page: React.FC = () => {
    const [dependencies, setDependencies] = useState<Dependency[]>([]);
    const [deployments, setDeployments] = useState<Deployment[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [user, setUser] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [message, setMessage] = useState<Message>(null);
    const [activeTab, setActiveTab] = useState<'upload' | 'deploy' | 'deployed'>('upload');

    const fetchData = useCallback(async () => {
        setIsLoading(true);
        setMessage(null);
        try {
            const [deps, deploys] = await Promise.all([
                mockFetch<Dependency[], void>('/api/dependencies', 'GET'),
                mockFetch<Deployment[], void>('/api/deployment', 'GET'),
            ]);
            setDependencies(deps);
            setDeployments(deploys);
        } catch (error: any) {
            setMessage({ 
                type: 'error', 
                text: 'Error loading initial data.', 
                details: [error.error || 'Check the console logs for more details.'] 
            });
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedFile || !user) {
            setMessage({ type: 'error', text: 'Please, introduce your username and select a .tar file.' });
            return;
        }

        setIsUploading(true);
        setMessage({ type: 'info', text: `Uploading ${selectedFile.name}...` });

        try {
            const response = await mockFetch<{ message: string }, { challengeFile: File }>('/api/dependencies', 'POST', { challengeFile: selectedFile });
            setMessage({ type: 'success', text: response.message });
            setSelectedFile(null);
            await fetchData();
        } catch (error: any) {
            setMessage({ 
                type: 'error', 
                text: 'Error uploading file.', 
                details: [error.error || 'Processing or network error.'] 
            });
        } finally {
            setIsUploading(false);
        }
    };

    // 3. Manejar el despliegue del desafío - POST /api/deployment
    const handleDeploy = useCallback(async (challengeName: string) => {
        if (!user) {
            setMessage({ type: 'error', text: 'Username is mandatory for the deployment.' });
            return;
        }
        
        // Simular un estado de carga mientras se despliega
        setDeployments(prev => [...prev, { release_name: `${user}-${challengeName}`, status: 'pending-upgrade', chart: challengeName }]);
        setMessage({ type: 'info', text: `Starting deployment of '${challengeName}' challenge for user '${user}'...` });

        const payload = {
            user_name: user,
            challenge_name: challengeName
        };

        try {
            const response = await mockFetch<{ message: string, release_name: string, helm_output: string[] }, typeof payload>('/api/deployment', 'POST', payload);
            
            setMessage({ 
                type: 'success', 
                text: response.message, 
                details: [`Release: ${response.release_name}`] 
            });
            await fetchData();
        } catch (error: any) {
             setMessage({ 
                type: 'error', 
                text: 'Error deploying the challenge.', 
                details: [error.error || 'Check the console logs for more details.'] 
            });
            setDeployments(prev => prev.map(d => 
                d.release_name === `${user}-${challengeName}` ? { ...d, status: 'error' } : d
            ));
        }
    }, [user, fetchData]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files ? e.target.files[0] : null;
        if (file && (file.name.endsWith('.tar') || file.name.endsWith('.tar.gz'))) {
            setSelectedFile(file);
            setMessage(null);
        } else {
            setSelectedFile(null);
            setMessage({ type: 'error', text: 'Only files with .tar or .tar.gz extensions are valid.' });
        }
    };

    const isDeploying = deployments.some(d => d.status === 'pending-upgrade');

    return (
        <div className="min-h-screen bg-gray-50 p-4 sm:p-8 font-sans">
            {/* Carga de Tailwind CSS para el entorno de la Immersive */}
            <script src="https://cdn.tailwindcss.com"></script> 
            <div className="max-w-4xl mx-auto">
                <header className="text-center mb-10">
                    <h1 className="text-4xl font-extrabold text-gray-900 flex items-center justify-center space-x-3">
                        <Server className="w-8 h-8 text-indigo-600" />
                        <span>Helm Challenge Manager</span>
                    </h1>
                    <p className="text-lg text-gray-600 mt-2">Upload and deploy CTF Challenges.</p>
                </header>

                <div className="bg-white p-6 rounded-xl shadow-2xl border border-gray-100">
                    <MessageBox message={message} />
                    
                    {/* Input de Usuario */}
                    <div className="mb-8">
                        <label htmlFor="user-input" className="block text-sm font-medium text-gray-700 mb-2">
                            Your username:
                        </label>
                        <input
                            id="user-input"
                            type="text"
                            value={user}
                            onChange={(e) => setUser(e.target.value)}
                            placeholder="e.g., hacker_01"
                            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                            required
                        />
                    </div>
                    
                    {/* Navigate through tabs */}
                    <div className="flex border-b border-gray-200 mb-6">
                        <TabButton 
                            active={activeTab === 'upload'} 
                            onClick={() => setActiveTab('upload')} 
                            icon={Upload}
                            label="Upload Challenge (.tar)" 
                        />
                        <TabButton 
                            active={activeTab === 'deploy'} 
                            onClick={() => setActiveTab('deploy')} 
                            icon={Send}
                            label="Deploy Challenge" 
                        />
                         <TabButton 
                            active={activeTab === 'deployed'} 
                            onClick={() => setActiveTab('deployed')} 
                            icon={List}
                            label="Active Deployments" 
                        />
                    </div>

                    {/* Contenido de la Pestaña */}
                    <div className="p-4">
                        {activeTab === 'upload' && (
                            <UploadSection 
                                user={user}
                                selectedFile={selectedFile}
                                handleFileChange={handleFileChange}
                                handleUpload={handleUpload}
                                isUploading={isUploading}
                            />
                        )}
                        {activeTab === 'deploy' && (
                            <DeploySection
                                isLoading={isLoading}
                                dependencies={dependencies}
                                user={user}
                                handleDeploy={handleDeploy}
                                fetchData={fetchData}
                                isDeploying={isDeploying}
                            />
                        )}
                         {activeTab === 'deployed' && (
                            <DeployedSection
                                isLoading={isLoading}
                                deployments={deployments}
                                fetchData={fetchData}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Page;