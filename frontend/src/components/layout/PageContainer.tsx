import React from 'react';

interface Props {
  children: React.ReactNode;
  className?: string;
}

export const PageContainer: React.FC<Props> = ({ children, className = '' }) => {
  return (
    <div className={`p-6 lg:p-8 space-y-8 max-w-7xl mx-auto w-full ${className}`}>
      {children}
    </div>
  );
};
