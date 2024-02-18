import { useState, useCallback } from "react";

// Custom hook to fetch and play audio, returning playback status
export const usePlayResponse = () => {
  const [isPlaying, setIsPlaying] = useState(false);

  const fetchAndPlayAudio = useCallback(async (text: string) => {
    setIsPlaying(false); // Reset playback status
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
      const audio = new Audio(url);

      audio.onended = () => setIsPlaying(false); // Update status when audio ends
      audio.onplay = () => setIsPlaying(true); // Update status when audio starts playing
      await audio.play();
    } catch (error) {
      console.error("Error fetching or playing audio:", error);
      setIsPlaying(false);
    }
  }, []);

  return { fetchAndPlayAudio, isPlaying };
};
