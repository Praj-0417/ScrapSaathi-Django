import { useState } from "react";
import {
  BuildingLibraryIcon,
  TruckIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  UsersIcon,
  CubeIcon,
} from "@heroicons/react/24/outline";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function RecycleCompanyDashboard() {
  const [view, setView] = useState("dashboard");
  const [dateFilter, setDateFilter] = useState("today");
  const [supplyStatus, setSupplyStatus] = useState("incoming");

  const supplySchedule = {
    incoming: [
      {
        id: "SUP-101",
        date: "2025-04-07",
        seller: "GreenBins Co.",
        material: "Plastic",
        qty: "500 kg",
        eta: "10:00 AM",
        status: "scheduled",
      },
      {
        id: "SUP-102",
        date: "2025-04-08",
        seller: "EcoWaste Ltd.",
        material: "Paper",
        qty: "300 kg",
        eta: "2:00 PM",
        status: "scheduled",
      },
    ],
    received: [
      {
        id: "SUP-090",
        date: "2025-04-05",
        seller: "RecycleNow",
        material: "Metal",
        qty: "200 kg",
        receivedBy: "Dock 3",
      },
      {
        id: "SUP-089",
        date: "2025-04-04",
        seller: "GreenBins Co.",
        material: "Glass",
        qty: "150 kg",
        receivedBy: "Dock 1",
      },
    ],
  };

  const performanceData = {
    today: {
      shipments: 2,
      processed: "800 kg",
      revenue: "₹12,000",
      suppliers: 2,
      capacity: "40%",
    },
    week: {
      shipments: 10,
      processed: "4,200 kg",
      revenue: "₹58,000",
      suppliers: 8,
      capacity: "60%",
    },
    month: {
      shipments: 40,
      processed: "16,000 kg",
      revenue: "₹200,000",
      suppliers: 25,
      capacity: "75%",
    },
  };

  const weeklyChartData = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    datasets: [
      {
        label: "Kg Processed",
        data: [500, 600, 550, 700, 650, 400, 300],
        backgroundColor: "#4CAF50",
      },
      {
        label: "Revenue (₹k)",
        data: [8, 9.5, 8.2, 10, 9, 6, 4],
        backgroundColor: "#2196F3",
      },
    ],
  };

  const materialDistData = {
    labels: ["Plastic", "Paper", "Metal", "Glass", "E-Waste"],
    datasets: [
      {
        data: [40, 25, 20, 10, 5],
        backgroundColor: [
          "#FF9800",
          "#9C27B0",
          "#F44336",
          "#2196F3",
          "#795548",
        ],
      },
    ],
  };

  const Navigation = () => (
    <div className="bg-white shadow-md p-4 mb-6 rounded-lg flex justify-center space-x-4">
      {["dashboard", "supply", "performance"].map((tab) => (
        <button
          key={tab}
          onClick={() => setView(tab)}
          className={`px-4 py-2 rounded-lg ${
            view === tab
              ? "bg-green-500 text-white"
              : "bg-gray-100 text-gray-700"
          }`}
        >
          {tab.charAt(0).toUpperCase() + tab.slice(1)}
        </button>
      ))}
    </div>
  );

  return (
    <div className="bg-gradient-to-r from-green-500 to-blue-500 min-h-screen p-8 mt-20">
      <div className="text-center text-white mb-8">
        <h1 className="text-4xl font-bold">Recycling Company Dashboard</h1>
        <p className="text-lg mt-2">
          Track supply, processing, and performance
        </p>
      </div>

      <Navigation />

      {view === "dashboard" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(performanceData.today).map(([key, value], i) => {
            const icons = [
              TruckIcon,
              CubeIcon,
              CurrencyDollarIcon,
              UsersIcon,
              BuildingLibraryIcon,
            ];
            const colors = [
              "text-green-500",
              "text-blue-500",
              "text-purple-500",
              "text-orange-500",
              "text-red-500",
            ];
            const Icon = icons[i];
            const color = colors[i];
            return (
              <div
                key={key}
                className="bg-white p-6 rounded-lg shadow-lg flex items-center space-x-4"
              >
                <Icon className={`w-10 h-10 ${color}`} />
                <div>
                  <p className="text-sm text-gray-500 uppercase">{key}</p>
                  <p className="text-2xl font-bold">{value}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {view === "supply" && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Supply Schedule</h2>
          <div className="flex space-x-4 mb-4">
            <button
              onClick={() => setSupplyStatus("incoming")}
              className={`px-4 py-2 rounded-lg ${
                supplyStatus === "incoming"
                  ? "bg-green-500 text-white"
                  : "bg-gray-100"
              }`}
            >
              Incoming
            </button>
            <button
              onClick={() => setSupplyStatus("received")}
              className={`px-4 py-2 rounded-lg ${
                supplyStatus === "received"
                  ? "bg-green-500 text-white"
                  : "bg-gray-100"
              }`}
            >
              Received
            </button>
          </div>
          <ul className="space-y-4">
            {(supplyStatus === "incoming"
              ? supplySchedule.incoming
              : supplySchedule.received
            ).map((s) => (
              <li
                key={s.id}
                className="border p-4 rounded-lg flex justify-between items-center"
              >
                <div>
                  <p className="font-medium">
                    {s.id} • {s.seller}
                  </p>
                  <p className="text-sm">
                    {s.date}{" "}
                    {s.eta ? `at ${s.eta}` : `• Received at ${s.receivedBy}`}
                  </p>
                  <p className="text-sm">
                    {s.material} – {s.qty}
                  </p>
                </div>
                {s.status && (
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                    {s.status}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {view === "performance" && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Performance Over Time</h2>
          <div className="flex space-x-2 mb-6">
            {["today", "week", "month"].map((period) => (
              <button
                key={period}
                onClick={() => setDateFilter(period)}
                className={`px-4 py-2 rounded-lg ${
                  dateFilter === period
                    ? "bg-green-500 text-white"
                    : "bg-gray-100"
                }`}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            {Object.entries(performanceData[dateFilter]).map(([key, value]) => (
              <div
                key={key}
                className="bg-green-50 p-4 rounded-lg text-center shadow"
              >
                <p className="text-sm uppercase text-gray-500">{key}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-gray-50 p-4 rounded-lg shadow">
              <h3 className="text-xl font-semibold mb-2 flex items-center">
                <ChartBarIcon className="w-5 h-5 mr-2 text-green-500" /> Weekly
                Throughput
              </h3>
              <Bar
                data={weeklyChartData}
                options={{
                  responsive: true,
                  plugins: { legend: { position: "top" } },
                }}
              />
            </div>
            <div className="bg-gray-50 p-4 rounded-lg shadow flex flex-col items-center">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <CubeIcon className="w-5 h-5 mr-2 text-blue-500" /> Material
                Distribution
              </h3>
              <div className="w-60 h-60">
                <Doughnut
                  data={materialDistData}
                  options={{ maintainAspectRatio: false }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
