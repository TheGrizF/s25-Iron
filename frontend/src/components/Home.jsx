import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/style.css'; // Import CSS from React frontend

const Home = ({ user }) => {
    return (
        <div>
            <div className="logo">
                <img src="/images/logo.png" alt="TasteBuddies Logo" />
            </div>
            
            <h1>Hello, {user?.username}!</h1>
            <div className="footer"></div>
            <h1>Welcome to TasteBuddies</h1>
            <p>Click the button below to add a new user to the database:</p>
            
            <Link to="/addUser">
                <button>Add User</button>
            </Link>
        </div>
    );
};

export default Home;
