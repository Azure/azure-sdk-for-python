import { DefaultButton } from "@fluentui/react";
import { useMsal } from "@azure/msal-react";
import { useTranslation } from "react-i18next";

import styles from "./LoginButton.module.css";
import { useState, useContext } from "react";
import { LoginContext } from "../../loginContext";

export const LoginButton = () => {
    const { instance } = useMsal();
    const { loggedIn, setLoggedIn } = useContext(LoginContext);
    const activeAccount = instance.getActiveAccount();
    const [username, setUsername] = useState("");
    const { t } = useTranslation();

    return (
        <DefaultButton
            text={loggedIn ? `${t("logout")}\n${username}` : `${t("login")}`}
            className={styles.loginButton}
            // onClick={loggedIn ? handleLogoutPopup : handleLoginPopup}
        ></DefaultButton>
    );
};
