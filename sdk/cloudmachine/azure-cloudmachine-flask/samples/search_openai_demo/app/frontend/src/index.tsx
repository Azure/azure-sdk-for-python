import React from "react";
import ReactDOM from "react-dom/client";
import { createHashRouter, RouterProvider } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import { HelmetProvider } from "react-helmet-async";
import { initializeIcons } from "@fluentui/react";

import "./index.css";

import Ask from "./pages/ask/Ask";
import LayoutWrapper from "./layoutWrapper";
import i18next from "./i18n/config";

initializeIcons();

const router = createHashRouter([
    {
        path: "/",
        element: <LayoutWrapper />,
        children: [
            {
                index: true,
                element: <Ask />
            },
            {
                path: "chat",
                lazy: () => import("./pages/chat/Chat")
            },
            {
                path: "*",
                lazy: () => import("./pages/NoPage")
            }
        ]
    }
]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <I18nextProvider i18n={i18next}>
            <HelmetProvider>
                <RouterProvider router={router} />
            </HelmetProvider>
        </I18nextProvider>
    </React.StrictMode>
);
