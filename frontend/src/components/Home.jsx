import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/style.css'; // Import CSS from React frontend

const Home = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.get('http://localhost:5000/api/users/get_by_email',  {
                params: { email }
            });

            console.log('Login Response:', response.data);

            if (response.data && !response.data.error) {
                console.log('Navigating to /welcome with user:', response.data);
                navigate('/welcome', { state: { user: response.data } });
            } else {
                alert('User not found.  Try again or Create a New Account.');
            }
        } catch (error) {
            console.error('Login failed:', error);
            alert('Error logging in.  Try again?');
        }
    };
    
    return (
        <div className="home-container">
          <img src="/images/logo.png" alt="TasteBuddies Logo" className="logo" />
          <h1>Welcome to TasteBuddies</h1>
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
            </div>
            <div className="form-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
            </div>
            <button type="submit">Login</button>
          </form>
          <p>
            Don’t have an account? <a href="/adduser">Create New User</a>
          </p>
        </div>
    );
};

export default Home;
