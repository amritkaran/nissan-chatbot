"use client";

import { ChevronRight, Car, Zap, Shield, Wrench } from "lucide-react";
import ChatWidget from "@/components/ChatWidget";
import Image from "next/image";

const vehicles = [
  {
    name: "Qashqai",
    tagline: "The Ultimate Crossover",
    price: "From £28,250",
    image: "https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/qashqai/j12/overview/packshots/my22-qashqai-3-4-front-passenger-side.png",
  },
  {
    name: "Juke",
    tagline: "Dare to be Different",
    price: "From £23,650",
    image: "https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/juke/f16e/overview/packshots/my21-juke-3-4-front-passenger-side.png",
  },
  {
    name: "Ariya",
    tagline: "100% Electric",
    price: "From £36,990",
    image: "https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/ariya/overview/packshots/my22-ariya-3-4-front-passenger-side.png",
  },
  {
    name: "X-Trail",
    tagline: "Adventure Awaits",
    price: "From £35,000",
    image: "https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/x-trail/t33/overview/packshots/my22-x-trail-3-4-front-passenger-side.png",
  },
];

const features = [
  {
    icon: Zap,
    title: "Electric Innovation",
    description: "Leading the charge with zero-emission technology",
  },
  {
    icon: Shield,
    title: "Safety First",
    description: "Advanced safety features to protect what matters most",
  },
  {
    icon: Wrench,
    title: "Expert Service",
    description: "Nationwide network of certified service centres",
  },
  {
    icon: Car,
    title: "Test Drive",
    description: "Book your test drive experience today",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-black text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <svg viewBox="0 0 200 30" className="h-6 w-auto fill-current">
                <text x="0" y="24" className="text-2xl font-bold tracking-widest">NISSAN</text>
              </svg>
            </div>

            {/* Nav Links */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#vehicles" className="text-sm uppercase tracking-wider hover:text-nissan-red transition-colors">
                Vehicles
              </a>
              <a href="#electric" className="text-sm uppercase tracking-wider hover:text-nissan-red transition-colors">
                Electric
              </a>
              <a href="#" className="text-sm uppercase tracking-wider hover:text-nissan-red transition-colors">
                Offers
              </a>
              <a href="#" className="text-sm uppercase tracking-wider hover:text-nissan-red transition-colors">
                Owners
              </a>
            </div>

            {/* CTA */}
            <a
              href="#"
              className="bg-nissan-red px-6 py-2 text-sm uppercase tracking-wider rounded-full hover:bg-red-700 transition-colors"
            >
              Book Test Drive
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen flex items-center">
        {/* Background Image */}
        <div className="absolute inset-0 bg-black">
          <div
            className="absolute inset-0 bg-cover bg-center opacity-70"
            style={{
              backgroundImage: "url('https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/ariya/overview/hero/my22-ariya-hero-background.jpg')",
            }}
          />
          <div className="absolute inset-0 hero-gradient" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 pt-16">
          <div className="max-w-2xl">
            <span className="inline-block px-4 py-1 bg-nissan-red text-white text-sm uppercase tracking-wider rounded-full mb-6">
              New Arrival
            </span>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Nissan Ariya
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-lg">
              Experience the future of mobility. 100% electric, 100% exhilarating.
              Up to 329 miles of range on a single charge.
            </p>
            <div className="flex flex-wrap gap-4">
              <a
                href="#"
                className="inline-flex items-center gap-2 bg-nissan-red text-white px-8 py-4 rounded-full uppercase tracking-wider font-medium hover:bg-red-700 transition-colors"
              >
                Discover More
                <ChevronRight className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="inline-flex items-center gap-2 border-2 border-white text-white px-8 py-4 rounded-full uppercase tracking-wider font-medium hover:bg-white hover:text-black transition-colors"
              >
                Build Yours
              </a>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/60">
          <span className="text-xs uppercase tracking-wider">Scroll</span>
          <div className="w-6 h-10 border-2 border-white/40 rounded-full flex justify-center pt-2">
            <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
          </div>
        </div>
      </section>

      {/* Vehicles Section */}
      <section id="vehicles" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-black mb-4">Our Vehicles</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Discover the perfect Nissan for your lifestyle. From efficient city cars to
              adventurous SUVs and pioneering electric vehicles.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {vehicles.map((vehicle) => (
              <div
                key={vehicle.name}
                className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-shadow group cursor-pointer"
              >
                <div className="aspect-[4/3] bg-gray-100 relative overflow-hidden">
                  <img
                    src={vehicle.image}
                    alt={vehicle.name}
                    className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-black mb-1">{vehicle.name}</h3>
                  <p className="text-gray-500 text-sm mb-3">{vehicle.tagline}</p>
                  <p className="text-nissan-red font-semibold">{vehicle.price}</p>
                  <a
                    href="#"
                    className="mt-4 inline-flex items-center text-sm font-medium text-black hover:text-nissan-red transition-colors"
                  >
                    Explore
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Electric Section */}
      <section id="electric" className="py-20 bg-black text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <span className="inline-block px-4 py-1 bg-nissan-red text-white text-sm uppercase tracking-wider rounded-full mb-6">
                Electric
              </span>
              <h2 className="text-4xl font-bold mb-6">
                The Future is Electric
              </h2>
              <p className="text-gray-400 mb-8 text-lg">
                Join the electric revolution with Nissan. Over 10 years of EV expertise,
                500,000+ electric vehicles sold, and a commitment to a sustainable future.
              </p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-nissan-red/20 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-nissan-red" />
                  </div>
                  <span>Up to 329 miles range</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-nissan-red/20 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-nissan-red" />
                  </div>
                  <span>Fast charging in 30 minutes</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-nissan-red/20 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-nissan-red" />
                  </div>
                  <span>Zero emissions, zero compromise</span>
                </li>
              </ul>
              <a
                href="#"
                className="inline-flex items-center gap-2 bg-nissan-red text-white px-8 py-4 rounded-full uppercase tracking-wider font-medium hover:bg-red-700 transition-colors"
              >
                Explore Electric
                <ChevronRight className="w-5 h-5" />
              </a>
            </div>
            <div className="relative">
              <img
                src="https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/leaf/ze1/overview/packshots/MY21-leaf-3-4-front-passenger-side.png"
                alt="Nissan LEAF"
                className="w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="text-center">
                <div className="w-16 h-16 bg-nissan-red/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-8 h-8 text-nissan-red" />
                </div>
                <h3 className="text-lg font-bold text-black mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            <div>
              <h4 className="font-bold uppercase tracking-wider mb-4">Vehicles</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Crossovers & SUVs</a></li>
                <li><a href="#" className="hover:text-white">Electric Vehicles</a></li>
                <li><a href="#" className="hover:text-white">Vans</a></li>
                <li><a href="#" className="hover:text-white">All Models</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold uppercase tracking-wider mb-4">Shop</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Build & Price</a></li>
                <li><a href="#" className="hover:text-white">Offers</a></li>
                <li><a href="#" className="hover:text-white">Finance</a></li>
                <li><a href="#" className="hover:text-white">Find a Dealer</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold uppercase tracking-wider mb-4">Owners</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Service & Parts</a></li>
                <li><a href="#" className="hover:text-white">Warranty</a></li>
                <li><a href="#" className="hover:text-white">Roadside Assistance</a></li>
                <li><a href="#" className="hover:text-white">Manuals & Guides</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold uppercase tracking-wider mb-4">About</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">About Nissan</a></li>
                <li><a href="#" className="hover:text-white">Sustainability</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              © 2024 Nissan. All rights reserved.
            </p>
            <div className="flex gap-6 text-sm text-gray-500">
              <a href="#" className="hover:text-white">Privacy Policy</a>
              <a href="#" className="hover:text-white">Terms of Use</a>
              <a href="#" className="hover:text-white">Cookie Settings</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget />
    </main>
  );
}
