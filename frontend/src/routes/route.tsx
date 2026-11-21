import { Navigate, useRoutes } from "react-router-dom";

import AnalysisPage from "../pages/Analysis";

export default function AppRoutes() {
  return useRoutes([
    { path: "/", element: <AnalysisPage /> },
    { path: "*", element: <Navigate to="/" replace /> },
  ]);
}
