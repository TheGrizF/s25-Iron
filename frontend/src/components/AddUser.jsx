import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/style.css'; // Import CSS from React frontend

const AddUser = () => {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: ''
    });

    const navigate = useNavigate()

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/api/users/add', formData, {
                headers: {
                    'Content-Type': 'application/json',
                },
                withCredentials: true
            });
            
            if (response.data && response.data.message)
                alert('User added successfully');
                navigate('/')
        } catch (error) {
            console.error('Error adding user:', error);
            if (error.response && error.response.status === 409) {
                alert('User already exists!');
            } else {
                alert('Smells Burnt.  Lets Try again.');
            }
        }
    };

    return (
      <div className="home-container">
        <img src="/images/logo.png" alt="TasteBuddies Logo" className="logo" />
        <h1>Create New User</h1>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <input
              type="text"
              name="firstName"
              placeholder="First Name"
              value={formData.firstName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              name="lastName"
              placeholder="Last Name"
              value={formData.lastName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit">Create Account</button>
        </form>
        <p>
          Already have an account? <a href="/">Return to Login</a>
        </p>
      </div>
    );
  };
  
  export default AddUser;