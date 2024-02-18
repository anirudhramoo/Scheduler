import { useState, FC } from "react";
import { SchedulerButtonSmall } from "./SchedulerButtonSmall";
import { SchedulerButtonLarge } from "./SchedulerButtonLarge";

import SlowTextRenderer from "./SlowTextRenderer";
import useMicrophone from "../../hooks/useMicrophone";
import { usePlayResponse } from "../../hooks/usePlayResponse";

type SchedulerState = "recording" | "analysing" | "done";

export type SchedulerProps = {
  profile: any;
};
export const Scheduler: FC<SchedulerProps> = ({ profile }) => {
  const [state, setState] = useState<SchedulerState>("done");
  const [data, setData] = useState<string>("");
  const [messages, setMessages] = useState<any[]>([]);

  const { fetchAndPlayAudio, isPlaying, stopAudio } = usePlayResponse();
  const sendAudioToAPI = async (
    audioBlob: Blob,
    messagesArr: any[]
  ): Promise<any> => {
    setState("analysing");
    try {
      const formData = new FormData();
      // console.log(audioBlob);
      formData.append("profile", JSON.stringify(profile));
      formData.append("prior_messages", JSON.stringify(messagesArr));
      formData.append("audio", audioBlob);
      console.log(messagesArr);
      const response = await fetch(
        process.env.REACT_APP_API_ENDPOINT + "/process-audio",
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();
      await fetchAndPlayAudio(result.text);

      // setting text
      setData(result.text ?? "");

      setMessages(result?.prior_messages);

      setState("done");
      return result;
    } catch (error) {
      setState("done");
      console.error("Failed to send audio:", error);
      throw error; // Re-throw to handle in the caller
    }
  };

  const { startRecording, stopAndSendRecording } = useMicrophone({
    sendAudioToAPI,
  });

  return (
    <div className="flex flex-col justify-center items-center h-screen pt-24">
      {state === "done" ? (
        <>
          <div className="mb-12">
            {data !== "" ? (
              <SlowTextRenderer text={data} />
            ) : (
              <h1 className="text-2xl font-bold">Talk to Heather!</h1>
            )}
          </div>
          <SchedulerButtonLarge
            onClick={() => {
              stopAudio();
              setState("recording");
              startRecording();
            }}
          />
        </>
      ) : state === "recording" ? (
        <>
          <div className="flex flex-col items-center justify-center mt-8 mb-24">
            <SchedulerButtonSmall
              onClick={async () => {
                await stopAndSendRecording(messages);
              }}
            />
            <h1 className=" mt-6 text-3xl font-bold">Listening</h1>
            <h2 className="text-white text-opacity-50 text-sm">
              Click the button above to finish
            </h2>
          </div>
          <button
            type="button"
            className="mt-4 bg-white bg-opacity-20  border  text-white font-bold py-2 px-8 rounded transition ease-in-out duration-300"
            onClick={() => {
              setData("");
              setState("done");
            }}
          >
            Cancel
          </button>
        </>
      ) : (
        <>
          <h1 className="animate-fade-in-out  text-lg font-medium">
            Analysing your request
          </h1>
          <SchedulerButtonLarge onClick={() => {}} />
        </>
      )}
    </div>
  );
};
