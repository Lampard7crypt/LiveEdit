import React from 'react';
import { useHandleSignInCallback } from '@logto/react';

const LogtoCallback: React.FC = () => {
  const { isLoading, error } = useHandleSignInCallback(() => {
    window.location.replace('/');
  });

  if (error) {
    return (
      <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center gap-4 p-6 text-center">
        <p role="alert">Sign-in failed: {error.message || 'Unable to complete authentication.'}</p>
        <a className="text-[#00ff41] underline" href="/">
          Return to Live Edit
        </a>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">
      {isLoading ? 'Completing sign-in…' : 'Redirecting…'}
    </div>
  );
};

export default LogtoCallback;
