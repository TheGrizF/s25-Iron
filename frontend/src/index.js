import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import AddUser from "./components/AddUser";
import Welcome from "./components/Welcome";
import "./styles/style.css"; // Import global styles

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/addUser" element={<AddUser />} />
                <Route path="/welcome" element={<Welcome />} />
            </Routes>
        </Router>
    );
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
