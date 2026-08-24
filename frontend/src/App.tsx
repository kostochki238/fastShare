import { useState, useEffect } from 'react'
import { useCookies } from "react-cookie"
import { Scanner } from '@yudiel/react-qr-scanner'
import QRCode from "react-qr-code"
import Files from './Files.tsx'

import './App.css'

function QR(session, setSession) {
  const [scan, setScan] = useState(false);
  const [paused, setPaused] = useState(false);
  if(scan) {
    return (
      <>
      <Scanner
        className="session-qr"
        onScan={(result) => setSession(result)}
        paused={paused}
      />
      <div className="button-group">
        <button className="scanner-toggle" onClick={() => setPaused(!paused)}>
          {paused ? "Resume" : "Pause"}
        </button>
        <button className="share-session" onClick={() => setScan(false)}>
          Share
        </button>
      </div>
      </>
    )
  } else {
    return (
      <>
      <QRCode
        className="session-qr"
        value={session}
      />
      <div className="button-group">
        <button className="scan-session" onClick={() => setScan(true)}>
          Connect
        </button>
      </div>
      </>
    )
  }
}

function App() {
  const [cookies, setCookies] = useCookies(['SESSION']);
  const [session, setSession] = useState(cookies.SESSION);
  useEffect(() => {
    const ctrl = new AbortController();
    const {signal} = ctrl;
    async function fetchSession(){
      try {
        if(!cookies.SESSION) {
          const resp = await fetch("/api/get/id", {signal, method: "HEAD"});
          if (resp.status_code == 200) setSession(cookies.SESSION);
        }
      } catch (error) {
        if (error !== 'AbortError') {
          console.log("Fetch error: ", error);
        }
      }
    }
    fetchSession();
    return () => {
      ctrl.abort();
    }
  }, []);
  return (
    <>
      <div className="session-info">
        <div className="session">
          <QR session={session} setSession={setSession}/>
        </div>
        <Files />
      </div>
    </>
  );
}

export default App
