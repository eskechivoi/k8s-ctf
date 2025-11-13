import React from 'react';
import { AlertTriangle, CheckCircle, Server } from 'lucide-react';
import type { Message } from '@/lib/types'; 

interface MessageBoxProps {
    message: Message;
}

/**
 * Shows feedback messages (success, error, info) to the user
 */
const MessageBox: React.FC<MessageBoxProps> = ({ message }) => {
    if (!message) return null;

    const Icon = message.type === 'success' ? CheckCircle : message.type === 'error' ? AlertTriangle : Server;
    const color = message.type === 'success' ? 'bg-green-50 border-green-400 text-green-800' : 
                  message.type === 'error' ? 'bg-red-50 border-red-400 text-red-800' : 
                  'bg-blue-50 border-blue-400 text-blue-800';

    return (
        <div className={`p-4 rounded-lg border ${color} mb-6 flex items-start space-x-3`}>
            <Icon className="w-5 h-5 flex-shrink-0 mt-1" />
            <div>
                <p className="font-bold">{message.text}</p>
                {message.details && message.details.length > 0 && (
                    <ul className="text-sm list-disc list-inside mt-1 space-y-0.5">
                        {message.details.map((detail, index) => <li key={index}>{detail}</li>)}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default MessageBox;