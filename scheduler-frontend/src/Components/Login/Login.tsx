import { GoogleOAuthProvider } from "@react-oauth/google";
import { Auth } from "./Auth";

export const Login = () => {
  return (
    <div className="flex flex-col justify-center items-center h-screen ">
      <h1 className="font-sans text-7xl font-bold mb-12">Meet Heather.ai</h1>
      <p className="animate-pulse font-sans text-2xl font-medium mb-12">
        Your virtual scheduling assistant!
      </p>
      <GoogleOAuthProvider
        clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID ?? ""}
      >
        <Auth />
      </GoogleOAuthProvider>
    </div>
  );
};
