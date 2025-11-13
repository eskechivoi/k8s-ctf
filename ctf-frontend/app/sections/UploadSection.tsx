import React from 'react';
import { Upload, RotateCw } from 'lucide-react';

interface UploadSectionProps {
    user: string;
    selectedFile: File | null;
    handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleUpload: (e: React.FormEvent) => Promise<void>;
    isUploading: boolean;
}

/**
 * Component to upload .tar files and add new challenges
 */
const UploadSection: React.FC<UploadSectionProps> = ({ user, selectedFile, handleFileChange, handleUpload, isUploading }) => (
    <>
        <h2 className="text-xl font-bold text-gray-800 mb-4">1. Upload Challenge</h2>
        <form onSubmit={handleUpload} className="space-y-4">
            <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-indigo-500 transition-colors duration-200">
                <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".tar,.tar.gz"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center justify-center">
                        <Upload className="w-10 h-10 text-indigo-400 mb-2" />
                        <p className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                            {selectedFile ? selectedFile.name : 'Click to select a .tar or .tar.gz file.'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Drag and drop is also valid.</p>
                    </div>
                </label>
            </div>
            <button
                type="submit"
                className={`w-full flex items-center justify-center py-3 px-4 border border-transparent rounded-lg shadow-md text-sm font-medium text-white transition duration-300 ${
                    !user || !selectedFile || isUploading 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                }`}
                disabled={!user || !selectedFile || isUploading}
            >
                {isUploading ? (
                    <RotateCw className="w-5 h-5 mr-2 animate-spin" />
                ) : (
                    <Upload className="w-5 h-5 mr-2" />
                )}
                {isUploading ? 'Uploading and processing...' : 'Upload and add challenge'}
            </button>
        </form>
    </>
);

export default UploadSection;