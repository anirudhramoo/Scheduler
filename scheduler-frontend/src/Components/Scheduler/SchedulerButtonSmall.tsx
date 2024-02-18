import { FC } from "react";
export type SchedulerButtonSmallProps = {
  onClick: () => void;
};

export const SchedulerButtonSmall: FC<SchedulerButtonSmallProps> = ({
  onClick,
}) => {
  return (
    <>
      <div
        className="radiating-circle mt-8 cursor-pointer bg-white bg-opacity-20 w-40 h-40 rounded-full overflow-hidden 
border-2 border-gray-300 animate-pulse"
        onClick={onClick}
      >
        {/* Logo goes here */}
      </div>
    </>
  );
};
