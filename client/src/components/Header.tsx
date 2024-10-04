import { FaCreditCard, FaInfoCircle, FaArrowRight } from "react-icons/fa";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="sticky top-0 bg-white/80 backdrop-blur-md z-50 shadow-md">
      {/* Top Banner */}
      <div className="flex justify-center items-center py-3 bg-gradient-to-r from-green-500 to-green-700 text-white text-sm gap-3">
        <p className="text-white/70 hidden md:block">
          Improve efficiency with this starter template
        </p>
        <Link to="/contact" className="inline-flex items-center gap-1">
          <p>Get Started</p>
          <FaArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Navbar */}
      <div className="container mx-auto flex justify-between items-center p-4">
        <Link to="/" className="text-xl font-bold text-primary">
          Starter template
        </Link>
        <nav className="flex space-x-6">
          <Link
            to="/services"
            className="flex items-center text-gray-700 hover:text-primary"
          >
            <FaCreditCard className="mr-2" />
            Services
          </Link>
          <Link
            to="/about"
            className="flex items-center text-gray-700 hover:text-primary"
          >
            <FaInfoCircle className="mr-2" />
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
