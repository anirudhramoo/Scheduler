import React, { useState, useEffect, FC } from "react";

export type SlowTextRendererProps = {
  text: string;
  wordDelay?: number;
};
const SlowTextRenderer: FC<SlowTextRendererProps> = ({
  text,
  wordDelay = 140,
}) => {
  const [currentText, setCurrentText] = useState("");
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const words = text.split(" "); // Split text into words

  useEffect(() => {
    if (currentWordIndex < words.length) {
      const timerId = setTimeout(() => {
        // Update the current text with the next word
        const newText =
          currentText + (currentText ? " " : "") + words[currentWordIndex];
        setCurrentText(newText);
        // Move to the next word
        setCurrentWordIndex(currentWordIndex + 1);
      }, wordDelay);

      // Cleanup timeout on component unmount or when currentWordIndex changes
      return () => clearTimeout(timerId);
    }
  }, [currentText, currentWordIndex, words]); // Update dependencies

  return (
    <div className="max-w-xl mx-auto ">
      <p className="text-md font-light text-white p-5  ">
        <span className="font-bold">Heather: </span> {currentText}
      </p>
    </div>
  );
};

export default SlowTextRenderer;
