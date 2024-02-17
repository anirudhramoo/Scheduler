import { useState, useCallback, useEffect, useRef } from 'react';

const useMicrophone = () => {
  const [status, setStatus] = useState<'idle' | 'recording' | 'denied' | 'sending' | 'sent'>('idle');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(() => {
    console.log("recording starting");
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        console.log("the stream");
        const recorder = new MediaRecorder(stream);
        mediaRecorderRef.current = recorder;

        recorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        recorder.start();
        setStatus('recording');
      })
      .catch(err => {
        console.error('Error accessing microphone:', err);
        setStatus('denied');
      });
  }, []);

  const stopAndSendRecording = useCallback(() => {
    const mediaRecorder = mediaRecorderRef.current;
    if (mediaRecorder) {
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/flac' });
        console.log(audioChunksRef.current);
        try {
          const response = await sendAudioToAPI(audioBlob);
          console.log(response);
          setStatus('sent');
          audioChunksRef.current = []; // Clear recorded chunks
        } catch (err) {
          console.error('Error sending audio to API:', err);
          setStatus('idle'); // Reset status on error
        } finally {
          setStatus('idle');
        }
      };
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop()); // Stop the media stream
      setStatus('sending');
    }
  }, []);

  return { startRecording, stopAndSendRecording, status };
};

async function sendAudioToAPI(audioBlob: Blob): Promise<any> {
  try {
    const response = await fetch('http://127.0.0.1:5000/process-audio', {
      method: 'POST',
      body: audioBlob,
    });
    const result = await response.json();
    console.log('Audio sent successfully', result);
    return result;
  } catch (error) {
    console.error('Failed to send audio:', error);
    throw error; // Re-throw to handle in the caller
  }
}

export default useMicrophone;
