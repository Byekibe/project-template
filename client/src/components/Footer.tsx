import { FaFacebook, FaTwitter, FaLinkedin } from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-6">
      <div className="container mx-auto text-center">
        <p>&copy; 2024 Starter template. All Rights Reserved.</p>
        <div className="flex justify-center mt-4 space-x-6">
          <a
            href="https://facebook.com"
            aria-label="Facebook"
            className="hover:text-gray-400"
          >
            <FaFacebook />
          </a>
          <a
            href="https://twitter.com"
            aria-label="Twitter"
            className="hover:text-gray-400"
          >
            <FaTwitter />
          </a>
          <a
            href="https://linkedin.com"
            aria-label="LinkedIn"
            className="hover:text-gray-400"
          >
            <FaLinkedin />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
