import { useState, useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import Cookies from "js-cookie";

export const Auth = () => {
  const getUserInfo = async (codeResponse: any) => {
    // modify api here
    var response = await fetch("http://127.0.0.1:3001/google_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code: codeResponse.code }),
    });

    return await response.json();
  };

  const [user, setUser] = useState<any>(undefined);
  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      let loginDetails = await getUserInfo(codeResponse);
      let token = loginDetails.headers.get("Authorization");

      setUser(loginDetails.user);
      localStorage.setItem("profile", JSON.stringify(loginDetails.user));
      localStorage.setItem("token", token);
    },
  });

  const handleLogout = () => {
    setUser(undefined);
    localStorage.removeItem("profile");
    localStorage.removeItem("token");
  };
  useEffect(() => {
    const profile = localStorage.getItem("profile");
    const token = localStorage.getItem("token");
    if (profile && token) {
      setUser(JSON.parse(profile));
    }
  }, []);
  return (
    <>
      {!user ? (
        <button
          type="button"
          className="bg-gray-100 text-orange-600  hover:bg-gray-200 focus:ring-4 focus:outline-none  font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center justify-between dark:focus:ring-[#4285F4]/55 mr-2 mb-2
       transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300"
          onClick={() => googleLogin()}
        >
          <svg
            className="mr-2 -ml-1 w-4 h-4"
            aria-hidden="true"
            focusable="false"
            data-prefix="fab"
            data-icon="google"
            role="img"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 488 512"
          >
            <path
              fill="currentColor"
              d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
            ></path>
          </svg>
          Sign up with Google<div></div>
        </button>
      ) : (
        <div className="flex">
          <img
            className="w-10 h-10 p-1 rounded-full   mr-2"
            src={user?.picture ?? ""}
            alt="Bordered avatar"
          />

          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
    </>
  );
};
