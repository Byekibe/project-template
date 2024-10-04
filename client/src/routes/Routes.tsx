import { createBrowserRouter, Link } from "react-router-dom";
import Contact from "../pages/contact";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <h1 className="text-4xl font-bold text-gray-800 mb-6">
          Starter Template
        </h1>
        <Link
          to="/contact"
          className="text-lg text-white bg-green-500 px-6 py-3 rounded-full hover:bg-green-600 transition duration-300"
        >
          Contact
        </Link>
      </div>
    ),
  },
  {
    path: "contact",
    element: <Contact />,
  },
]);

export default router;
