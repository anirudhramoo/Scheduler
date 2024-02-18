import { useState } from "react";
import { SchedulerButtonSmall } from "./SchedulerButtonSmall";
import { SchedulerButtonLarge } from "./SchedulerButtonLarge";

type SchedulerState = "recording" | "analysing" | "done";
export const Scheduler = () => {
  const [state, setState] = useState<SchedulerState>("done");

  return (
    <div className="flex flex-col justify-center items-center h-screen pt-24">
      {state === "done" ? (
        <>
          <h1 className=" text-2xl font-bold">Click to Schedule</h1>
          <SchedulerButtonLarge onClick={() => setState("recording")} />
        </>
      ) : state === "recording" ? (
        <>
          <div className="flex flex-col items-center justify-center mt-8 mb-24">
            <SchedulerButtonSmall onClick={() => setState("analysing")} />
            <h1 className=" mt-6 text-3xl font-bold">Listening</h1>
            <h2 className="text-white text-opacity-50 text-sm">
              Click the button above to finish
            </h2>
          </div>
          <button
            type="button"
            className="mt-4 bg-white bg-opacity-20  border  text-white font-bold py-2 px-8 rounded transition ease-in-out duration-300"
            onClick={() => setState("done")}
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
