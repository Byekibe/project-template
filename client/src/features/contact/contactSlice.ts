import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface Contact {
  name: string;
  email: string;
  message: string;
}

interface ContactResponse {
  msg: string;
}

// Define the base URL for your API
const baseUrl = import.meta.env.VITE_BASE_URL;

export const contactApiSlice = createApi({
  baseQuery: fetchBaseQuery({ baseUrl }),
  reducerPath: "contactApi",
  endpoints: (build) => ({
    createContact: build.mutation<ContactResponse, Contact>({
      query: (contactData) => ({
        url: "/contact",
        method: "POST",
        body: contactData,
      }),
    }),
  }),
});

export const { useCreateContactMutation } = contactApiSlice;
