import { useState, useCallback } from "react";

// Custom hook to fetch and play audio, returning playback status and a function to stop the audio
export const usePlayResponse = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState<any>(null); // State to hold the Audio object

  const fetchAndPlayAudio = useCallback(
    async (text: string) => {
      setIsPlaying(false); // Reset playback status
      // Stop and clean up any existing audio before starting a new one
      if (audio) {
        audio.pause();
        URL.revokeObjectURL(audio.src);
        setAudio(null);
      }
      try {
        const response = await fetch("https://api.openai.com/v1/audio/speech", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${process.env.REACT_APP_OPENAI_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "tts-1",
            input: text,
            voice: "nova",
          }),
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const newAudio = new Audio(url);

        newAudio.onended = () => {
          setIsPlaying(false); // Update status when audio ends
          URL.revokeObjectURL(url); // Clean up the object URL
        };
        newAudio.onplay = () => setIsPlaying(true); // Update status when audio starts playing
        setAudio(newAudio); // Save the Audio object in state
        await newAudio.play();
      } catch (error) {
        console.error("Error fetching or playing audio:", error);
        setIsPlaying(false);
      }
    },
    [audio]
  );

  // Function to stop audio playback
  const stopAudio = useCallback(() => {
    if (audio) {
      audio.pause();
      audio.currentTime = 0; // Reset audio to start
      setIsPlaying(false);
    }
  }, [audio]);

  return { fetchAndPlayAudio, stopAudio, isPlaying };
};
