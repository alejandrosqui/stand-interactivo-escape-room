import { AdminPage } from "./AdminPage";
import { HomePage } from "./HomePage";
import { ParticipantPage } from "./ParticipantPage";

export default function App() {
  const path = window.location.pathname.split("/").filter(Boolean);

  if (path[0] === "admin") return <AdminPage />;
  if (path[0] === "experiencia" && path[1]) {
    return <ParticipantPage codigo={path[1]} />;
  }
  return <HomePage />;
}

