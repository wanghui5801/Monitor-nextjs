import React from 'react';

interface StatusBadgeProps {
    status: 'Running' | 'Stopped' | 'Error';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
    const getStatusConfig = () => {
        switch (status) {
            case 'Running':
                return {
                    color: 'bg-gradient-to-r from-emerald-500 to-green-500 dark:from-emerald-600 dark:to-green-600',
                    icon: (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    )
                };
            case 'Stopped':
                return {
                    color: 'bg-gradient-to-r from-red-500 to-rose-500 dark:from-red-600 dark:to-rose-600',
                    icon: (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    )
                };
            default:
                return {
                    color: 'bg-gradient-to-r from-yellow-500 to-amber-500 dark:from-yellow-600 dark:to-amber-600',
                    icon: (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    )
                };
        }
    };

    const { color, icon } = getStatusConfig();

    return (
        <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium text-white
            shadow-sm transition-all duration-300 hover:scale-105 ${color}`}>
            {icon}
            <span>{status}</span>
        </span>
    );
};

export default StatusBadge;
