import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import AddUser from "./components/AddUser";
import "./styles/style.css"; // Import global styles

const App = () => {
    return (
        <div className="app-container">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/addUser" element={<AddUser />} />
            </Routes>
        </div>
    );
};

export default App;
