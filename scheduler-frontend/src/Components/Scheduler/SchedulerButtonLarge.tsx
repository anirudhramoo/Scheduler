import { FC } from "react";
export type SchedulerButtonLargeProps = {
  onClick: () => void;
};

export const SchedulerButtonLarge: FC<SchedulerButtonLargeProps> = ({
  onClick,
}) => {
  return (
    <>
      <div
        className="mt-8 cursor-pointer bg-white bg-opacity-20 w-56 h-56 rounded-full overflow-hidden 
border-2 border-gray-300 animate-pulse flex justify-center items-center"
        onClick={onClick}
      >
        <img src="/logo.png" alt="Descriptive Alt Text" className="w-24" />
      </div>
    </>
  );
};
