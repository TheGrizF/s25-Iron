import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/style.css'; // Import CSS from React frontend

const AddUser = () => {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/addUser', formData); // Adjust backend API endpoint if needed
            alert('User added successfully');
            setFormData({ firstName: '', lastName: '', email: '' }); // Reset form
        } catch (error) {
            console.error('Error adding user:', error);
            alert('Error adding user. Please try again.');
        }
    };

    return (
        <div>
            <h1>Add User</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor="firstName">First Name:</label><br />
                <input type="text" id="firstName" name="firstName" value={formData.firstName} onChange={handleChange} required /><br /><br />

                <label htmlFor="lastName">Last Name:</label><br />
                <input type="text" id="lastName" name="lastName" value={formData.lastName} onChange={handleChange} required /><br /><br />

                <label htmlFor="email">Email:</label><br />
                <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} required /><br /><br />

                <button type="submit">Submit</button>
            </form>
            <br />
            <Link to="/">
                <button>Go Back to Homepage</button>
            </Link>
        </div>
    );
};

export default AddUser;
