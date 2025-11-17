import React from 'react';
import { Upload, Loader2, Send } from 'lucide-react';

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
    <form onSubmit={handleUpload} className="space-y-6">
        <div className="border border-dashed border-gray-300 rounded-xl p-8 text-center bg-gray-50 hover:bg-gray-100 transition duration-150">
            <Upload className="w-10 h-10 mx-auto text-indigo-400 mb-3" />
            <label htmlFor="file-upload" className="cursor-pointer">
                <p className="font-medium text-indigo-600 hover:text-indigo-500">
                    {selectedFile ? selectedFile.name : 'Click to select a .tar, .tar.gz or .tgz file'}
                </p>
                <p className="text-sm text-gray-500">Max size 10MB</p>
                <input 
                    id="file-upload" 
                    type="file" 
                    accept=".tar,.tar.gz" 
                    onChange={handleFileChange} 
                    className="hidden" 
                />
            </label>
        </div>

        <button
            type="submit"
            disabled={!user || !selectedFile || isUploading}
            className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 transition duration-150 ease-in-out transform hover:scale-[1.005]"
        >
            {isUploading ? (
                <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Uploading...
                </>
            ) : (
                <>
                    <Send className="w-5 h-5 mr-2" />
                    Upload Challenge
                </>
            )}
        </button>
        {!user && <p className="text-sm text-red-500 text-center">Please enter your username above to enable upload.</p>}
    </form>
);
export default UploadSection;