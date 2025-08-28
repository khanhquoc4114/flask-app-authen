import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const access_token = localStorage.getItem("access_token");
    const token_type = localStorage.getItem("token_type") || "bearer";
    if (access_token) {
      config.headers.Authorization = `${token_type} ${access_token}`;
    }
  }
  return config;
});

export default api;
