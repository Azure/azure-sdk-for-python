import { AccountInfo, EventType, PublicClientApplication } from "@azure/msal-browser";
import { checkLoggedIn, useLogin } from "./authConfig";
import { useEffect, useState } from "react";
import { MsalProvider } from "@azure/msal-react";
import { LoginContext } from "./loginContext";
import Layout from "./pages/layout/Layout";

const LayoutWrapper = () => {
    const [loggedIn, setLoggedIn] = useState(false);
    return (
        <LoginContext.Provider
            value={{
                loggedIn,
                setLoggedIn
            }}
        >
            <Layout />
        </LoginContext.Provider>
    );
};

export default LayoutWrapper;
