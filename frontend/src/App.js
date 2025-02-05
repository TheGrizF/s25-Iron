import React, { useState } from "react";
import Login from "./Login";
import BottomNav from "./BottomNav";

function App() {
  const [page, setPage] = useState(0);

  return (
    <div>
      {page === 0 && <h1>Home Page</h1>}
      {page === 1 && <h1>Profile Page</h1>}
      {page === 2 && <h1>Settings Page</h1>}
      
      <BottomNav onChange={setPage} />
    </div>
  );
}

export default App;
