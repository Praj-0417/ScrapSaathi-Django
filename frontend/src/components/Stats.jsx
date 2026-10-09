import React from "react";

function Stats() {
  return (
    <section className="py-20 bg-gray-100">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-semibold text-gray-800">
          Waste Collection Stats
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12 mt-12">
          <div className="bg-white shadow-xl rounded-lg p-8 hover:scale-105 transition-transform duration-300">
            <h3 className="text-xl font-semibold text-gray-800">
              Total Waste Collected
            </h3>
            <p className="text-3xl mt-4 text-green-600 font-bold">
              1,000+ Tons
            </p>
          </div>
          <div className="bg-white shadow-xl rounded-lg p-8 hover:scale-105 transition-transform duration-300">
            <h3 className="text-xl font-semibold text-gray-800">
              Recycling Rate
            </h3>
            <p className="text-3xl mt-4 text-blue-600 font-bold">75%</p>
          </div>
          <div className="bg-white shadow-xl rounded-lg p-8 hover:scale-105 transition-transform duration-300">
            <h3 className="text-xl font-semibold text-gray-800">
              Communities Served
            </h3>
            <p className="text-3xl mt-4 text-purple-600 font-bold">50+</p>
          </div>
          <div className="bg-white shadow-xl rounded-lg p-8 hover:scale-105 transition-transform duration-300">
            <h3 className="text-xl font-semibold text-gray-800">
              Projects Completed
            </h3>
            <p className="text-3xl mt-4 text-red-600 font-bold">200+</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Stats;
