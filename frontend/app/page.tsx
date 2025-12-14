"use client";

import { ChevronRight, Car, Zap, Shield, Wrench, Menu, Search, User } from "lucide-react";
import ChatWidget from "@/components/ChatWidget";
import { useState } from "react";

const vehicles = [
  {
    name: "Qashqai",
    tagline: "The Original Crossover",
    price: "From £28,250",
    image: "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&q=80",
    badge: "e-POWER",
  },
  {
    name: "Juke",
    tagline: "Small Hybrid SUV",
    price: "From £23,650",
    image: "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&q=80",
    badge: "Hybrid",
  },
  {
    name: "Ariya",
    tagline: "100% Electric Crossover",
    price: "From £36,990",
    image: "https://images.unsplash.com/photo-1619976215249-0b72a5b63acb?w=800&q=80",
    badge: "Electric",
  },
  {
    name: "X-Trail",
    tagline: "7-Seat Family SUV",
    price: "From £35,000",
    image: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80",
    badge: "e-POWER",
  },
  {
    name: "LEAF",
    tagline: "100% Electric Hatchback",
    price: "From £28,995",
    image: "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800&q=80",
    badge: "Electric",
  },
  {
    name: "Townstar",
    tagline: "Compact Van",
    price: "From £24,750",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
    badge: "EV Available",
  },
];

const navItems = [
  { label: "Vehicles", href: "#vehicles" },
  { label: "Electric", href: "#electric" },
  { label: "Offers", href: "#offers" },
  { label: "Owners", href: "#owners" },
  { label: "Shop Online", href: "#shop" },
];

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <main className="min-h-screen bg-white">
      {/* Top Bar */}
      <div className="bg-[#1a1a1a] text-white text-xs py-2 hidden md:block">
        <div className="max-w-7xl mx-auto px-6 flex justify-end gap-6">
          <a href="#" className="hover:text-gray-300">Find a Dealer</a>
          <a href="#" className="hover:text-gray-300">Contact Us</a>
          <a href="#" className="hover:text-gray-300">Build & Price</a>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="sticky top-0 z-40 bg-black text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 md:px-6">
          <div className="flex items-center justify-between h-16 md:h-20">
            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* Logo */}
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                {/* Nissan Logo */}
                <svg viewBox="0 0 100 100" className="h-12 w-12 md:h-14 md:w-14">
                  <circle cx="50" cy="50" r="48" fill="none" stroke="white" strokeWidth="2"/>
                  <rect x="10" y="42" width="80" height="16" fill="white"/>
                  <text x="50" y="55" textAnchor="middle" className="text-[11px] font-bold fill-black tracking-widest">NISSAN</text>
                </svg>
              </a>
            </div>

            {/* Desktop Nav Links */}
            <div className="hidden md:flex items-center gap-8">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="text-sm font-medium hover:text-nissan-red transition-colors py-2 border-b-2 border-transparent hover:border-nissan-red"
                >
                  {item.label}
                </a>
              ))}
            </div>

            {/* Right Icons */}
            <div className="flex items-center gap-4">
              <button className="p-2 hover:text-nissan-red transition-colors">
                <Search className="w-5 h-5" />
              </button>
              <button className="p-2 hover:text-nissan-red transition-colors hidden md:block">
                <User className="w-5 h-5" />
              </button>
              <a
                href="#"
                className="hidden md:inline-flex bg-nissan-red px-6 py-2.5 text-sm font-medium rounded hover:bg-red-700 transition-colors"
              >
                Book a Test Drive
              </a>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[#1a1a1a] border-t border-gray-800">
            <div className="px-4 py-4 space-y-3">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="block py-2 text-sm font-medium hover:text-nissan-red"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.label}
                </a>
              ))}
              <a
                href="#"
                className="block mt-4 bg-nissan-red px-6 py-3 text-sm font-medium rounded text-center"
              >
                Book a Test Drive
              </a>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative h-[70vh] md:h-[85vh] flex items-center overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1920&q=80"
            alt="Nissan Qashqai"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 w-full">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 bg-nissan-red text-white text-xs font-bold px-4 py-2 rounded mb-6">
              <Zap className="w-4 h-4" />
              NOW WITH e-POWER
            </div>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4 leading-tight">
              Nissan<br />Qashqai
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 leading-relaxed">
              The original crossover, now electrified. Experience the unique
              e-POWER technology for instant acceleration and ultimate efficiency.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <a
                href="#"
                className="inline-flex items-center justify-center gap-2 bg-nissan-red text-white px-8 py-4 font-medium hover:bg-red-700 transition-colors"
              >
                Discover More
                <ChevronRight className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 font-medium hover:bg-gray-100 transition-colors"
              >
                Build Yours
              </a>
            </div>
            <p className="mt-6 text-sm text-gray-400">
              From £28,250 | 5.3L/100km Combined | 118g/km CO₂
            </p>
          </div>
        </div>
      </section>

      {/* Quick Links Bar */}
      <section className="bg-[#f5f5f5] border-b">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-gray-300">
            {[
              { icon: Car, label: "Find a Dealer", desc: "Locate your nearest" },
              { icon: Zap, label: "Electric Vehicles", desc: "Explore our EV range" },
              { icon: Wrench, label: "Book a Service", desc: "Expert care for your car" },
              { icon: Shield, label: "Finance Options", desc: "Flexible payment plans" },
            ].map((item, i) => (
              <a
                key={i}
                href="#"
                className="flex items-center gap-4 p-6 hover:bg-gray-200 transition-colors"
              >
                <item.icon className="w-8 h-8 text-nissan-red" />
                <div>
                  <div className="font-semibold text-black">{item.label}</div>
                  <div className="text-sm text-gray-600">{item.desc}</div>
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Vehicles Section */}
      <section id="vehicles" className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-black mb-2">Explore Our Range</h2>
              <p className="text-gray-600">Find the perfect Nissan for you</p>
            </div>
            <a href="#" className="text-nissan-red font-medium flex items-center gap-1 mt-4 md:mt-0 hover:underline">
              View all vehicles <ChevronRight className="w-4 h-4" />
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {vehicles.map((vehicle) => (
              <div
                key={vehicle.name}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 group"
              >
                <div className="relative aspect-[16/10] bg-gradient-to-b from-gray-100 to-gray-50 overflow-hidden">
                  {vehicle.badge && (
                    <span className={`absolute top-4 left-4 px-3 py-1 text-xs font-bold rounded ${
                      vehicle.badge === 'Electric' ? 'bg-blue-600 text-white' :
                      vehicle.badge === 'e-POWER' ? 'bg-nissan-red text-white' :
                      'bg-gray-800 text-white'
                    }`}>
                      {vehicle.badge}
                    </span>
                  )}
                  <img
                    src={vehicle.image}
                    alt={vehicle.name}
                    className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-2xl font-bold text-black mb-1">{vehicle.name}</h3>
                  <p className="text-gray-500 text-sm mb-4">{vehicle.tagline}</p>
                  <p className="text-lg font-semibold text-black mb-4">{vehicle.price}</p>
                  <div className="flex gap-3">
                    <a
                      href="#"
                      className="flex-1 text-center bg-nissan-red text-white py-3 font-medium hover:bg-red-700 transition-colors text-sm"
                    >
                      Discover
                    </a>
                    <a
                      href="#"
                      className="flex-1 text-center border border-black text-black py-3 font-medium hover:bg-black hover:text-white transition-colors text-sm"
                    >
                      Build & Price
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Electric Banner */}
      <section id="electric" className="relative py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1920&q=80"
            alt="Nissan Electric"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/60" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded mb-6">
              <Zap className="w-4 h-4" />
              100% ELECTRIC
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              The Future is Electric
            </h2>
            <p className="text-xl text-gray-200 mb-8">
              Over 10 years of EV expertise. Over 500,000 electric vehicles sold.
              Join the electric revolution with Nissan Ariya and LEAF.
            </p>
            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white">329</div>
                <div className="text-sm text-gray-400">Miles Range*</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white">30</div>
                <div className="text-sm text-gray-400">Min Fast Charge</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white">0</div>
                <div className="text-sm text-gray-400">Emissions</div>
              </div>
            </div>
            <a
              href="#"
              className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 font-medium hover:bg-gray-100 transition-colors"
            >
              Explore Electric Range
              <ChevronRight className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      {/* Why Nissan */}
      <section className="py-16 md:py-24 bg-[#f5f5f5]">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-black text-center mb-12">Why Choose Nissan?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 text-center">
              <div className="w-16 h-16 bg-nissan-red/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-nissan-red" />
              </div>
              <h3 className="text-xl font-bold text-black mb-3">5 Year Warranty</h3>
              <p className="text-gray-600">
                Every new Nissan comes with a comprehensive 5-year/100,000 mile warranty for complete peace of mind.
              </p>
            </div>
            <div className="bg-white p-8 text-center">
              <div className="w-16 h-16 bg-nissan-red/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="w-8 h-8 text-nissan-red" />
              </div>
              <h3 className="text-xl font-bold text-black mb-3">EV Pioneers</h3>
              <p className="text-gray-600">
                Over a decade of electric vehicle innovation. The Nissan LEAF remains one of the world's best-selling EVs.
              </p>
            </div>
            <div className="bg-white p-8 text-center">
              <div className="w-16 h-16 bg-nissan-red/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Car className="w-8 h-8 text-nissan-red" />
              </div>
              <h3 className="text-xl font-bold text-black mb-3">British Built</h3>
              <p className="text-gray-600">
                Proudly manufacturing in Sunderland since 1986. The Qashqai and LEAF are built right here in the UK.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Offers Section */}
      <section id="offers" className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="relative rounded-lg overflow-hidden group">
              <img
                src="https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&q=80"
                alt="Nissan Offers"
                className="w-full h-80 object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              <div className="absolute bottom-0 left-0 p-8">
                <span className="inline-block bg-nissan-red text-white text-xs font-bold px-3 py-1 mb-3">
                  LIMITED OFFER
                </span>
                <h3 className="text-2xl font-bold text-white mb-2">0% APR Finance</h3>
                <p className="text-gray-300 mb-4">Available on selected models</p>
                <a href="#" className="text-white font-medium flex items-center gap-1 hover:underline">
                  View offers <ChevronRight className="w-4 h-4" />
                </a>
              </div>
            </div>
            <div className="relative rounded-lg overflow-hidden group">
              <img
                src="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80"
                alt="Test Drive"
                className="w-full h-80 object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              <div className="absolute bottom-0 left-0 p-8">
                <span className="inline-block bg-black text-white text-xs font-bold px-3 py-1 mb-3">
                  EXPERIENCE
                </span>
                <h3 className="text-2xl font-bold text-white mb-2">Book a Test Drive</h3>
                <p className="text-gray-300 mb-4">Try before you buy at your local dealer</p>
                <a href="#" className="text-white font-medium flex items-center gap-1 hover:underline">
                  Book now <ChevronRight className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <div className="col-span-2 md:col-span-1">
              {/* Logo */}
              <svg viewBox="0 0 100 100" className="h-16 w-16 mb-6">
                <circle cx="50" cy="50" r="48" fill="none" stroke="white" strokeWidth="2"/>
                <rect x="10" y="42" width="80" height="16" fill="white"/>
                <text x="50" y="55" textAnchor="middle" className="text-[11px] font-bold fill-black tracking-widest">NISSAN</text>
              </svg>
              <p className="text-sm text-gray-400">
                Innovation that excites
              </p>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Vehicles</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Crossovers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Electric</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Vans</a></li>
                <li><a href="#" className="hover:text-white transition-colors">All Models</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Shop</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Build & Price</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Offers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Finance</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Find a Dealer</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Owners</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Warranty</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Roadside Assist</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Manuals</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-wider mb-4">About</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About Nissan</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Sustainability</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              © 2024 Nissan Motor (GB) Ltd. All rights reserved.
            </p>
            <div className="flex gap-6 text-sm text-gray-500">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Use</a>
              <a href="#" className="hover:text-white transition-colors">Cookies</a>
              <a href="#" className="hover:text-white transition-colors">Accessibility</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget />
    </main>
  );
}
