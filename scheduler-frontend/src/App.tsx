import React from "react";
import "./index.css";
import { Login } from "./Components/Login/Login";
import { Scheduler } from "./Components/Scheduler/Scheduler";

function App() {
  async function getDummy() {
    let response = await fetch("http://127.0.0.1:3001/protected", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${""}`,
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    console.log(response);
  }
  return (
    <div className="w-screen h-screen  bg-gradient-to-r from-pink-500 to-orange-500 text-white">
      <div className="flex justify-start items-center h-24 w-full bg-white bg-opacity-20 absolute top-0 border-b border-gray-300">
        <img src="/logo.png" alt="Descriptive Alt Text" className="w-16 ml-8" />
      </div>
      {/* <Login /> */}
      <Scheduler />
    </div>
  );
}

export default App;
