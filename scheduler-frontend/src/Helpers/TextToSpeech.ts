export const fetchAndPlayAudio = async (text: string) => {
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

    // Get the Blob from the response
    const blob = await response.blob();

    // Convert the Blob to a URL
    const url = URL.createObjectURL(blob);

    // Create a new HTMLAudioElement and play the audio
    const audio = new Audio(url);
    audio.play();
  } catch (error) {
    console.error("Error fetching or playing audio:", error);
  }
};
