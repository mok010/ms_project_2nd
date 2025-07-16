import React from 'react';

const LoadingDots = () => {
  return (
    <div className="flex justify-start items-center py-4">
      <div className="w-8 h-8 bg-gradient-to-r from-[#667eea] to-[#764ba2] rounded-full shadow-lg animate-breathing">
        <div className="w-full h-full bg-white bg-opacity-20 rounded-full animate-ping"></div>
      </div>
      
      <style jsx>{`
        @keyframes breathing {
          0%, 100% {
            transform: scale(0.7);
            opacity: 0.7;
          }
          50% {
            transform: scale(1.0);
            opacity: 1;
          }
        }
        
        .animate-breathing {
          animation: breathing 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default LoadingDots;