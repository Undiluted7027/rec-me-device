import Layout from "./pages/Layout";
import Home from "./pages/Home";
// import About from "./pages/About";
// import Tech from "./pages/Tech";
// import Login from "./pages/Login";
// import Register from "./pages/Register";
// import NoPage from "./pages/NoPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "../src/static/styles/App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />}></Route>
          {/* <Route path="about" element={<About />}></Route>
          <Route path="tech" element={<Tech />}></Route>
          <Route path="login" element={<Login />}></Route>
          <Route path="register" element={<Register />}></Route>
          <Route path="*" element={<NoPage />}></Route> */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
