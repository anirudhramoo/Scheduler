import { useState, useCallback, useEffect, useRef } from "react";

type UseMicrophoneProps = {
  sendAudioToAPI: (input1: any, input2: any) => void;
};
const useMicrophone = ({ sendAudioToAPI }: UseMicrophoneProps) => {
  const [status, setStatus] = useState<
    "idle" | "recording" | "denied" | "sending" | "sent"
  >("idle");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(() => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        const recorder = new MediaRecorder(stream);
        mediaRecorderRef.current = recorder;

        recorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        recorder.start();
        setStatus("recording");
      })
      .catch((err) => {
        console.error("Error accessing microphone:", err);
        setStatus("denied");
      });
  }, []);

  const stopAndSendRecording = useCallback((messages: any[]) => {
    const mediaRecorder = mediaRecorderRef.current;
    if (mediaRecorder) {
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/flac",
        });
        console.log(audioChunksRef.current);
        try {
          await sendAudioToAPI(audioBlob, messages);

          audioChunksRef.current = []; // Clear recorded chunks
        } catch (err) {
          console.error("Error sending audio to API:", err);
          setStatus("idle"); // Reset status on error
        } finally {
          setStatus("idle");
        }
      };
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop()); // Stop the media stream
      setStatus("sending");
    }
  }, []);

  return { startRecording, stopAndSendRecording, status };
};

export default useMicrophone;
