import React from "react";
import {
  AcademicCapIcon,
  TruckIcon,
  ArrowPathIcon,
  LightBulbIcon,
} from "@heroicons/react/24/solid";

function Features() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-semibold text-gray-800">Our Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12 mt-12">
          {/* Sustainable Solutions Card */}
          <div className="bg-white shadow-xl rounded-lg p-8 flex flex-col justify-between h-full hover:scale-105 hover:shadow-2xl transition-transform duration-300">
            <div className="flex justify-center mb-6">
              <AcademicCapIcon className="h-16 w-16 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">
              Sustainable Solutions
            </h3>
            <p className="mt-4 text-lg text-gray-600 flex-grow">
              Eco-friendly waste management solutions for homes and businesses,
              reducing environmental footprint.
            </p>
          </div>

          {/* On-Demand Pickup Card */}
          <div className="bg-white shadow-xl rounded-lg p-8 flex flex-col justify-between h-full hover:scale-105 hover:shadow-2xl transition-transform duration-300">
            <div className="flex justify-center mb-6">
              <TruckIcon className="h-16 w-16 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">
              On-Demand Pickup
            </h3>
            <p className="mt-4 text-lg text-gray-600 flex-grow">
              Request waste pickups through our user-friendly platform and get
              timely, reliable service.
            </p>
          </div>

          {/* Expert Recycling Card */}
          <div className="bg-white shadow-xl rounded-lg p-8 flex flex-col justify-between h-full hover:scale-105 hover:shadow-2xl transition-transform duration-300">
            <div className="flex justify-center mb-6">
              <ArrowPathIcon className="h-16 w-16 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">
              Expert Recycling
            </h3>
            <p className="mt-4 text-lg text-gray-600 flex-grow">
              We ensure that all collected waste is sorted and sent to recycling
              centers to minimize landfill waste.
            </p>
          </div>

          {/* New Feature Card */}
          <div className="bg-white shadow-xl rounded-lg p-8 flex flex-col justify-between h-full hover:scale-105 hover:shadow-2xl transition-transform duration-300">
            <div className="flex justify-center mb-6">
              <LightBulbIcon className="h-16 w-16 text-yellow-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">
              Innovative Solutions
            </h3>
            <p className="mt-4 text-lg text-gray-600 flex-grow">
              Our innovative approach to waste management focuses on technology
              and creative solutions for a cleaner future.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Features;
