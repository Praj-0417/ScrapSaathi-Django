import { useState } from "react";
import {
  BriefcaseIcon,
  DocumentTextIcon,
  TruckIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import { Line, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register chart components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function BigOrganizationDashboard() {
  const [view, setView] = useState("dashboard");

  // Summary data
  const summary = {
    contracts: 3,
    volume: "23,000 kg",
    earnings: "₹1,200,000",
    pickups: 4,
    invoicesDue: 2,
  };

  // Monthly sales data
  const salesData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [
      {
        label: "Volume Sold (kg)",
        data: [4000, 4500, 3800, 5000, 4700, 4300],
        borderColor: "#4CAF50",
        backgroundColor: "rgba(76,175,80,0.2)",
        tension: 0.4,
      },
    ],
  };

  // Material distribution
  const distData = {
    labels: ["Plastic", "Paper", "Metal", "Glass", "E-Waste"],
    datasets: [
      {
        data: [45, 25, 15, 10, 5],
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

  // Contracts list
  const contracts = [
    {
      id: "CT-1001",
      material: "Plastic",
      volume: "10,000 kg",
      status: "Active",
      renewal: "2025-12-01",
    },
    {
      id: "CT-1002",
      material: "Paper",
      volume: "5,000 kg",
      status: "Pending",
      renewal: "2025-06-15",
    },
    {
      id: "CT-1003",
      material: "Metal",
      volume: "8,000 kg",
      status: "Active",
      renewal: "2026-01-10",
    },
  ];

  // Pickups schedule
  const pickups = [
    {
      id: "PU-2001",
      date: "2025-05-10",
      time: "09:00 AM",
      location: "HQ Warehouse",
    },
    {
      id: "PU-2002",
      date: "2025-05-15",
      time: "02:00 PM",
      location: "Secondary Site",
    },
    {
      id: "PU-2003",
      date: "2025-05-20",
      time: "11:00 AM",
      location: "Remote Facility",
    },
  ];

  // Navigation
  const Navigation = () => (
    <div className="bg-white shadow-md p-4 mb-6 rounded-lg flex justify-center space-x-4">
      {["dashboard", "contracts", "pickups"].map((tab) => (
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
      {/* Header */}
      <div className="text-center text-white mb-8">
        <h1 className="text-4xl font-bold">Enterprise Seller Dashboard</h1>
        <p className="text-lg mt-2">Manage contracts, sales, and pickups</p>
      </div>

      <Navigation />

      {/* Dashboard View */}
      {view === "dashboard" && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <BriefcaseIcon className="w-8 h-8 mx-auto text-green-500" />
              <p className="mt-2">Contracts</p>
              <p className="text-2xl font-bold">{summary.contracts}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <ChartBarIcon className="w-8 h-8 mx-auto text-blue-500" />
              <p className="mt-2">Volume Sold</p>
              <p className="text-2xl font-bold">{summary.volume}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <CurrencyDollarIcon className="w-8 h-8 mx-auto text-purple-500" />
              <p className="mt-2">Earnings</p>
              <p className="text-2xl font-bold">{summary.earnings}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <TruckIcon className="w-8 h-8 mx-auto text-orange-500" />
              <p className="mt-2">Pickups</p>
              <p className="text-2xl font-bold">{summary.pickups}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <DocumentTextIcon className="w-8 h-8 mx-auto text-red-500" />
              <p className="mt-2">Invoices Due</p>
              <p className="text-2xl font-bold">{summary.invoicesDue}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4">Sales Trend</h2>
              <Line
                data={salesData}
                options={{
                  responsive: true,
                  plugins: { legend: { position: "top" } },
                }}
              />
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4">
                Material Distribution
              </h2>
              <Doughnut data={distData} />
            </div>
          </div>
        </>
      )}

      {/* Contracts View */}
      {view === "contracts" && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Active Contracts</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2">Contract ID</th>
                <th className="p-2">Material</th>
                <th className="p-2">Volume</th>
                <th className="p-2">Status</th>
                <th className="p-2">Renewal Date</th>
              </tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="p-2">{c.id}</td>
                  <td className="p-2">{c.material}</td>
                  <td className="p-2">{c.volume}</td>
                  <td className="p-2 capitalize">{c.status}</td>
                  <td className="p-2">{c.renewal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pickups View */}
      {view === "pickups" && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Upcoming Pickups</h2>
          <ul className="space-y-4">
            {pickups.map((p) => (
              <li
                key={p.id}
                className="border p-4 rounded-lg flex justify-between items-center"
              >
                <div>
                  <p className="font-medium">
                    {p.id} • {p.location}
                  </p>
                  <p className="text-sm">
                    {p.date} at {p.time}
                  </p>
                </div>
                <ClockIcon className="w-6 h-6 text-green-500" />
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
