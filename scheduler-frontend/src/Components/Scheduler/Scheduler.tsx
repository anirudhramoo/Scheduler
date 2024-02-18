import { useState, FC } from "react";
import { SchedulerButtonSmall } from "./SchedulerButtonSmall";
import { SchedulerButtonLarge } from "./SchedulerButtonLarge";
import { fetchAndPlayAudio } from "../../Helpers/TextToSpeech";
import SlowTextRenderer from "./SlowTextRenderer";
import { MdAssistant } from "react-icons/md";

type SchedulerState = "recording" | "analysing" | "done";

export type SchedulerProps = {
  profile: any;
};
export const Scheduler: FC<SchedulerProps> = ({ profile }) => {
  const [state, setState] = useState<SchedulerState>("done");
  const [data, setData] = useState("");

  const getData = async () => {
    let response = await fetch("http://127.0.0.1:5000/protected", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ profile: profile }),
    });
    let { data } = await response.json();

    setData(data);
    await fetchAndPlayAudio(data);
    setState("done");
  };

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
          <SchedulerButtonLarge onClick={() => setState("recording")} />
        </>
      ) : state === "recording" ? (
        <>
          <div className="flex flex-col items-center justify-center mt-8 mb-24">
            <SchedulerButtonSmall
              onClick={() => {
                getData();
                setState("analysing");
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
