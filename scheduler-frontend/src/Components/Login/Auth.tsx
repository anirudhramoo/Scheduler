import { useState, useEffect, FC } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import Cookies from "js-cookie";
import { hasGrantedAllScopesGoogle } from "@react-oauth/google";

export type AuthProps = {
  setProfile: any;
};
export const Auth: FC<AuthProps> = ({ setProfile }) => {
  const getUserInfo = async (codeResponse: any) => {
    // modify api here
    var response = await fetch(
      process.env.REACT_APP_API_ENDPOINT + "/google_login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: codeResponse.code }),
      }
    );

    return await response.json();
  };

  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    scope:
      "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid https://www.googleapis.com/auth/calendar",
    onSuccess: async (codeResponse) => {
      let loginDetails = await getUserInfo(codeResponse);
      const hasAccess = hasGrantedAllScopesGoogle(
        loginDetails,
        "https://www.googleapis.com/auth/calendar"
      );
      console.log(hasAccess);
      console.log(loginDetails);
      localStorage.setItem("profile", JSON.stringify(loginDetails));
      setProfile(loginDetails);
    },
  });

  return (
    <>
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
    </>
  );
};
