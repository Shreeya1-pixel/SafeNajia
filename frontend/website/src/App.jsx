import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "./components/Toast";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import MessageScan from "./pages/nigeria/MessageScan";
import LinkScan from "./pages/nigeria/LinkScan";
import FraudCall from "./pages/nigeria/FraudCall";
import SimSwap from "./pages/nigeria/SimSwap";
import ChatDemo from "./pages/nigeria/ChatDemo";
import Cases from "./pages/nigeria/Cases";
import Analyze from "./pages/nigeria/Analyze";
import "./styles/safeo.css";
import "./styles/safenaija.css";

export default function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/messages" element={<MessageScan />} />
            <Route path="/chat-demo" element={<ChatDemo />} />
            <Route path="/links" element={<LinkScan />} />
            <Route path="/calls" element={<FraudCall />} />
            <Route path="/sim-swap" element={<SimSwap />} />
            <Route path="/cases" element={<Cases />} />
            {/* Legacy paths redirect into merged lab / messages */}
            <Route path="/lab" element={<SimSwap />} />
            <Route path="/languages" element={<MessageScan />} />
            <Route path="/intelligence" element={<Cases />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ToastProvider>
  );
}
