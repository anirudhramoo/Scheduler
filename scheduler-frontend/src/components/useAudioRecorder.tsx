import React from 'react';
import useMicrophone from './useMicrophone'; // Adjust the import path as needed

const AudioRecorder = () => {
  const { startRecording, stopAndSendRecording, status } = useMicrophone();

  return (
    <div>
      <button onClick={startRecording} disabled={status !== 'idle'}>Start Recording</button>
      <button onClick={stopAndSendRecording} disabled={status !== 'recording'}>Stop and Send</button>
      <p>Status: {status}</p>
    </div>
  );
};

export default AudioRecorder;
