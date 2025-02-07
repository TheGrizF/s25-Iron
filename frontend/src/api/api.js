import axios from 'axios';

// Set your Flask API base URL
const API_BASE_URL = 'http://localhost:5000/api';

export const getUser = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/users/user`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user:', error);
  }
};

export const addUser = async (userData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/users/add`, userData);
    return response.data;
  } catch (error) {
    console.error('Error adding user:', error);
  }
};
