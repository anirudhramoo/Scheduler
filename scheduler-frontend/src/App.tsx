import React from "react";
import "./index.css";
import { Login } from "./Components/Login/Login";
import { Scheduler } from "./Components/Scheduler/Scheduler";
import { useState, useEffect } from "react";

function App() {
  const [profile, setProfile] = useState<any>(undefined);

  useEffect(() => {
    const profile = localStorage.getItem("profile");
    if (profile) {
      setProfile(JSON.parse(profile));
    }
  }, []);

  const handleLogout = () => {
    setProfile(undefined);
    localStorage.removeItem("profile");
  };

  return (
    <div className="w-screen h-screen  bg-gradient-to-r from-pink-500 to-orange-500 text-white">
      <div className=" flex justify-between items-center h-24 w-full bg-white bg-opacity-20 absolute top-0 border-b border-gray-300">
        <img
          src="/text_logo.png"
          alt="Descriptive Alt Text"
          className="w-44 ml-8"
        />

        {profile && (
          <div className="flex mr-10">
            <img
              className="w-10 h-10 p-1 rounded-full   mr-2"
              src={profile?.user_info?.picture ?? ""}
              alt="Bordered avatar"
            />
            <button
              onClick={handleLogout}
              className="text-white border border-white px-4 rounded transition duration-300 ease-in-out hover:bg-white hover:text-black"
            >
              Logout
            </button>
          </div>
        )}
      </div>
      {!profile ? (
        <Login setProfile={setProfile} />
      ) : (
        <Scheduler profile={profile} />
      )}

      {!profile && (
        <div className="flex items-center h-12 w-full bg-white bg-opacity-20 absolute bottom-0 border-t border-gray-300  shadow-md">
          <a
            className="text-white font-medium  ml-6 mr-4 cursor-pointer hover:text-slate-200"
            href="https://airtable.com/app7vdcIUagvg3HsW/shrLtZyCrPSFqjjxS"
          >
            Want to be informed when this goes public?
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
