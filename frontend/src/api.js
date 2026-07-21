import axios from 'axios';

// Create a custom axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add a request interceptor to inject the JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle 401s (token expiry)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If the error is 401 Unauthorized, the token might be expired.
    // In a full app, we would use the refresh_token here to get a new access_token.
    // For now, if we get a 401, we just throw it so the AuthContext can log the user out.
    if (error.response && error.response.status === 401) {
       // Could trigger a custom event here to force logout in React
       window.dispatchEvent(new Event('auth-error'));
    }
    return Promise.reject(error);
  }
);

export default api;
