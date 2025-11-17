import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import type { Message } from '@/lib/types'; 

interface MessageBoxProps {
    message: Message;
}

/**
 * Shows feedback messages (success, error, info) to the user
 */
const MessageBox: React.FC<MessageBoxProps> = ({ message }) => {
    if (!message) return null;

    const Icon = message.type === 'error' 
        ? AlertTriangle 
        : message.type === 'success' 
            ? CheckCircle 
            : Info;
    
    const colors = {
        error: 'bg-red-100 text-red-800 border-red-300',
        success: 'bg-green-100 text-green-800 border-green-300',
        info: 'bg-blue-100 text-blue-800 border-blue-300',
    };

    return (
        <div className={`p-4 mb-6 rounded-xl border-l-4 ${colors[message.type]} shadow-inner`} role="alert">
            <div className="flex items-start">
                <Icon className={`w-5 h-5 mr-3 flex-shrink-0 mt-0.5 ${message.type === 'error' ? 'text-red-500' : message.type === 'success' ? 'text-green-500' : 'text-blue-500'}`} />
                <div className="flex-grow">
                    <p className="font-semibold">{message.text}</p>
                    {message.details && message.details.length > 0 && (
                        <ul className="mt-2 list-disc list-inside text-sm">
                            {message.details.map((detail, index) => (
                                <li key={index} className="text-gray-700/80">{detail}</li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBox;