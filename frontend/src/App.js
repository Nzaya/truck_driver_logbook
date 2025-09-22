import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [tripForm, setTripForm] = useState({
    current_location: "",
    pickup_location: "",
    dropoff_location: "",
    current_cycle_used: "",
  });

  const [routeInfo, setRouteInfo] = useState(null);
  const [entries, setEntries] = useState([]);

  // ===== Handle Trip Form =====
  const handleTripChange = (e) => {
    setTripForm({ ...tripForm, [e.target.name]: e.target.value });
  };

  const handleTripSubmit = (e) => {
    e.preventDefault();
    console.log("Submitting trip:", tripForm);

    axios
      // .post("http://127.0.0.1:8000/trip/", tripForm)
      // For deployment
      .post("https://truck-driver-logbook.onrender.com/trip/", tripForm) 

      .then((res) => {
        console.log("Trip planned:", res.data);
        setRouteInfo(res.data.route_info);

        // ✅ Flatten entries (since backend groups them by day → logs)
        const flattened = (res.data.entries || []).flatMap((day) => day.logs);
        setEntries(flattened);
      })
      .catch((err) => console.error("Error planning trip:", err));
  };

  // ===== Map duty status → Y-axis position =====
  const statusY = {
    OFF_DUTY: 30,
    SLEEPER: 70,
    DRIVING: 110,
    ON_DUTY: 150,
  };

  // ===== Convert entries into polyline points =====
  const linePoints = entries
    .map((e) => {
      if (!e.time || !e.duty_status) return null;
      const [hh, mm] = e.time.split(":").map(Number);
      const x = ((hh * 60 + (mm || 0)) / (24 * 60)) * 520; // 520px = 24h
      const y = statusY[e.duty_status] || 0;
      return `${x},${y}`;
    })
    .filter(Boolean)
    .join(" ");

  // ===== Calculate total hours spent in each status =====
  const calculateHours = (logs) => {
    let hoursByStatus = { OFF_DUTY: 0, SLEEPER: 0, DRIVING: 0, ON_DUTY: 0 };

    for (let i = 0; i < logs.length - 1; i++) {
      const current = logs[i];
      const next = logs[i + 1];

      if (!current.time || !next.time) continue;

      const [ch, cm] = current.time.split(":").map(Number);
      const [nh, nm] = next.time.split(":").map(Number);

      const start = ch + (cm || 0) / 60;
      const end = nh + (nm || 0) / 60;

      const diff = Math.max(0, end - start);
      hoursByStatus[current.duty_status] += diff;
    }

    // If last entry is missing, assume remainder of the day is that status
    if (logs.length > 0) {
      const last = logs[logs.length - 1];
      const [lh] = last.time.split(":").map(Number);
      hoursByStatus[last.duty_status] += 24 - lh;
    }

    return hoursByStatus;
  };

  const totals = calculateHours(entries);
  const totalHours = Object.values(totals).reduce((a, b) => a + b, 0);

  return (
    <div className="App">
      <h1>Driver’s Daily Log</h1>

      {/* ===== Trip Planner Section ===== */}
      <div className="trip-planner">
        <h2>Plan a Trip</h2>
        <form onSubmit={handleTripSubmit} className="trip-form">
          <input
            type="text"
            name="current_location"
            placeholder="Current Location"
            value={tripForm.current_location}
            onChange={handleTripChange}
          />
          <input
            type="text"
            name="pickup_location"
            placeholder="Pickup Location"
            value={tripForm.pickup_location}
            onChange={handleTripChange}
          />
          <input
            type="text"
            name="dropoff_location"
            placeholder="Dropoff Location"
            value={tripForm.dropoff_location}
            onChange={handleTripChange}
          />
          <input
            type="number"
            name="current_cycle_used"
            placeholder="Current Cycle Used (hrs)"
            value={tripForm.current_cycle_used}
            onChange={handleTripChange}
          />
          <button type="submit">Generate Log</button>
        </form>
      </div>

      {/* ===== Route Info Display ===== */}
      {routeInfo && (
        <div className="route-info">
          <h3>Route Information</h3>
          <p>
            From <strong>{routeInfo.from}</strong> → Pickup{" "}
            <strong>{routeInfo.pickup}</strong> → Dropoff{" "}
            <strong>{routeInfo.dropoff}</strong>
          </p>
          <p>
            Distance: {routeInfo.distance_miles} miles | Duration:{" "}
            {routeInfo.est_hours} hrs
          </p>
          <div>
            <strong>Fuel Stops:</strong>
            <ul>
              {routeInfo.fuel_stops.map((stop, idx) => (
                <li key={idx}>{stop}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* ===== Log Graph Section ===== */}
      {entries.length > 0 && (
        <>
          <h2>Logbook Graph</h2>
          <svg className="log-graph" width="700" height="200">
            {/* Horizontal duty status lines + labels + totals */}
            {Object.keys(statusY).map((status, i) => (
              <g key={i}>
                {/* Left labels */}
                <text
                  x="5"
                  y={statusY[status] + 4}
                  fontSize="12"
                  textAnchor="start"
                  className="status-label"
                >
                  {status.replace("_", " ")}
                </text>

                {/* Horizontal line */}
                <line
                  x1="80"
                  y1={statusY[status]}
                  x2="600"
                  y2={statusY[status]}
                  className="duty-line"
                />

                {/* Right totals */}
                <text
                  x="640"
                  y={statusY[status] + 4}
                  fontSize="12"
                  textAnchor="start"
                  className="hours-label"
                >
                  {totals[status].toFixed(1)}h
                </text>
              </g>
            ))}

            {/* Vertical hour markers */}
            {[...Array(25)].map((_, h) => (
              <g key={h}>
                <line
                  x1={80 + (h / 24) * 520}
                  y1={20}
                  x2={80 + (h / 24) * 520}
                  y2={160}
                  className="hour-line"
                />
                <text x={80 + (h / 24) * 520} y={175} className="hour-label">
                  {h}
                </text>
              </g>
            ))}

            {/* Polyline (driver's log line) */}
            <polyline
              points={linePoints}
              className="log-line"
              transform="translate(80,0)"
            />
          </svg>

          {/* Total Hours Summary */}
          <div className="total-hours">
            <strong>Total Hours: {totalHours.toFixed(1)}</strong> (Hours)
          </div>
        </>
      )}

      {/* ===== Remarks Section ===== */}
      {entries.length > 0 && (
        <div className="remarks">
          <h3>Remarks</h3>
          <ul>
            {entries.map((e, idx) => (
              <li key={idx}>
                {e.time} @ {e.location} → {e.remarks}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
