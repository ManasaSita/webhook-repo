import React, { useState, useEffect } from "react";

function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      fetch("http://localhost:5000/events")
        .then((res) => res.json())
        .then((data) => setEvents(data));
    };

    fetchData();
    const intervalId = setInterval(fetchData, 15000); // Poll every 15 seconds

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  return (
    <div className="App">
      <h1>GitHub Events</h1>
      <ul>
        {events.map((event, index) => (
          <li key={index}>
            {event.author} performed {event.action} on {event.repo} at {new Date(event.timestamp).toLocaleString()}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
