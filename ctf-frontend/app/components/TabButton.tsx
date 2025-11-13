import React from 'react';

interface TabButtonProps {
    active: boolean;
    onClick: () => void;
    icon: React.ElementType;
    label: string;
}

/**
 * Navigation button to change between tabs.
 */
const TabButton: React.FC<TabButtonProps> = ({ active, onClick, icon: Icon, label }) => {
    return (
        <button
            onClick={onClick}
            className={`flex-1 flex items-center justify-center py-3 px-1 text-sm font-medium transition-all duration-200 ease-in-out ${
                active 
                    ? 'text-indigo-600 border-b-2 border-indigo-600' 
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
        >
            <Icon className="w-5 h-5 mr-2" />
            {label}
        </button>
    );
};

export default TabButton;