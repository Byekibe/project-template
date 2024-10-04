import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useCreateContactMutation } from "../features/contact/contactSlice";
import { SerializedError } from "@reduxjs/toolkit";
import { FetchBaseQueryError } from "@reduxjs/toolkit/query";

// Define the shape of the error response
interface ErrorResponse {
  msg: string;
}

const ContactForm = () => {
  // Validation schema
  const validationSchema = Yup.object().shape({
    name: Yup.string().required("Name is required"),
    email: Yup.string()
      .email("Please enter a valid email")
      .required("Email is required"),
    message: Yup.string().required("Message is required"),
  });

  // Create mutation hook for contact
  const [createContact, { isLoading, isSuccess, isError, error }] =
    useCreateContactMutation();

  // Type guard to check if error is FetchBaseQueryError
  const isFetchBaseQueryError = (
    error: unknown
  ): error is FetchBaseQueryError => {
    return typeof error === "object" && error !== null && "data" in error;
  };

  // Type guard to check if error is SerializedError
  const isSerializedError = (error: unknown): error is SerializedError => {
    return typeof error === "object" && error !== null && "message" in error;
  };

  return (
    <section id="contact" className="py-16 bg-white">
      <div className="container mx-auto text-center">
        <h2 className="text-3xl font-bold mb-4">Contact Us</h2>
        <p className="mb-8 text-gray-600">
          Feel free to reach out for any inquiries or support. We're here to
          help!
        </p>

        <Formik
          initialValues={{ name: "", email: "", message: "" }}
          validationSchema={validationSchema}
          onSubmit={async (values, { setSubmitting, resetForm }) => {
            try {
              const response = await createContact(values).unwrap();
              console.log("Response: ", response);
              alert("Your message has been sent!");
              resetForm(); // Reset form after successful submission
            } catch (err) {
              console.error("Failed to send message:", err);
            } finally {
              setSubmitting(false);
            }
          }}
        >
          {({ isSubmitting }) => (
            <Form className="max-w-md mx-auto space-y-6">
              <div className="flex flex-col">
                <Field
                  type="text"
                  name="name"
                  placeholder="Enter your name"
                  className="p-3 border border-gray-300 rounded"
                />
                <ErrorMessage
                  name="name"
                  component="div"
                  className="text-red-500 text-sm mt-1"
                />
              </div>

              <div className="flex flex-col">
                <Field
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  className="p-3 border border-gray-300 rounded"
                />
                <ErrorMessage
                  name="email"
                  component="div"
                  className="text-red-500 text-sm mt-1"
                />
              </div>

              <div className="flex flex-col">
                <Field
                  as="textarea"
                  name="message"
                  placeholder="Write your message"
                  className="p-3 border border-gray-300 rounded h-32"
                />
                <ErrorMessage
                  name="message"
                  component="div"
                  className="text-red-500 text-sm mt-1"
                />
              </div>

              <button
                type="submit"
                className="bg-green-500 text-white py-3 px-6 rounded-full hover:bg-green-600 transition duration-300"
                disabled={isSubmitting || isLoading}
              >
                {isSubmitting || isLoading ? "Sending..." : "Send Message"}
              </button>

              {/* Display feedback for errors or success */}
              {isSuccess && (
                <p className="text-green-500 mt-4">
                  Your message has been sent successfully!
                </p>
              )}
              {isError && (
                <p className="text-red-500 mt-4">
                  {isFetchBaseQueryError(error) &&
                  (error.data as ErrorResponse)?.msg
                    ? (error.data as ErrorResponse).msg
                    : isSerializedError(error) && error.message
                    ? error.message
                    : "Something went wrong. Please try again."}
                </p>
              )}
            </Form>
          )}
        </Formik>
      </div>
    </section>
  );
};

export default ContactForm;
