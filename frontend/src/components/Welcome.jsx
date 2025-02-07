import React from 'react';
import { useLocation, useNavigate} from 'react-router-dom';
import '../styles/style.css';

const Welcome = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = location.state || {};

    console.log('User Data:', user);

    if (!user) {
        return (
        <div className="home-container">
            <h1>Who are you? Did you <a href="/">login</a>? You should <a href="/">login</a>.</h1>
        </div>
        );
    }

    return (
        <div className='home-container'>
            <img src='/images/logo.png' alt='TasteBuddies Logo' className='logo' />
            <h1>Welcome, {user.firstName} {user.lastName}!</h1>
            <p>Email: {user.email}</p>
            <button onClick={() => navigate('/')}>Logout</button>
        </div>
    );
};

export default Welcome;