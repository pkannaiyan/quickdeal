'use client';

import { useState, useEffect, useRef } from 'react';

interface Location {
  city: string;
  pincode: string;
  state: string;
  lat: number;
  lng: number;
}

interface LocationPickerProps {
  currentPincode: string;
  currentCity: string;
  onLocationChange: (location: Location) => void;
  isOpen: boolean;
  onClose: () => void;
}

// Major cities in India with their pincodes and coordinates
const CITIES: Location[] = [
  { city: "Mumbai", pincode: "400001", state: "Maharashtra", lat: 19.0760, lng: 72.8777 },
  { city: "Mumbai - Andheri", pincode: "400053", state: "Maharashtra", lat: 19.1136, lng: 72.8697 },
  { city: "Mumbai - Bandra", pincode: "400050", state: "Maharashtra", lat: 19.0596, lng: 72.8295 },
  { city: "Mumbai - Powai", pincode: "400076", state: "Maharashtra", lat: 19.1176, lng: 72.9060 },
  { city: "Delhi", pincode: "110001", state: "Delhi", lat: 28.6139, lng: 77.2090 },
  { city: "Delhi - Connaught Place", pincode: "110001", state: "Delhi", lat: 28.6315, lng: 77.2167 },
  { city: "Delhi - Dwarka", pincode: "110075", state: "Delhi", lat: 28.5921, lng: 77.0460 },
  { city: "Gurgaon", pincode: "122001", state: "Haryana", lat: 28.4595, lng: 77.0266 },
  { city: "Noida", pincode: "201301", state: "Uttar Pradesh", lat: 28.5355, lng: 77.3910 },
  { city: "Bangalore", pincode: "560001", state: "Karnataka", lat: 12.9716, lng: 77.5946 },
  { city: "Bangalore - Koramangala", pincode: "560034", state: "Karnataka", lat: 12.9352, lng: 77.6245 },
  { city: "Bangalore - Whitefield", pincode: "560066", state: "Karnataka", lat: 12.9698, lng: 77.7500 },
  { city: "Bangalore - HSR Layout", pincode: "560102", state: "Karnataka", lat: 12.9116, lng: 77.6389 },
  { city: "Hyderabad", pincode: "500001", state: "Telangana", lat: 17.3850, lng: 78.4867 },
  { city: "Hyderabad - Hitech City", pincode: "500081", state: "Telangana", lat: 17.4435, lng: 78.3772 },
  { city: "Hyderabad - Gachibowli", pincode: "500032", state: "Telangana", lat: 17.4401, lng: 78.3489 },
  { city: "Chennai", pincode: "600001", state: "Tamil Nadu", lat: 13.0827, lng: 80.2707 },
  { city: "Chennai - T Nagar", pincode: "600017", state: "Tamil Nadu", lat: 13.0418, lng: 80.2341 },
  { city: "Chennai - Adyar", pincode: "600020", state: "Tamil Nadu", lat: 13.0012, lng: 80.2565 },
  { city: "Pune", pincode: "411001", state: "Maharashtra", lat: 18.5204, lng: 73.8567 },
  { city: "Pune - Hinjewadi", pincode: "411057", state: "Maharashtra", lat: 18.5912, lng: 73.7380 },
  { city: "Pune - Kothrud", pincode: "411038", state: "Maharashtra", lat: 18.5074, lng: 73.8077 },
  { city: "Kolkata", pincode: "700001", state: "West Bengal", lat: 22.5726, lng: 88.3639 },
  { city: "Kolkata - Salt Lake", pincode: "700091", state: "West Bengal", lat: 22.5800, lng: 88.4200 },
  { city: "Ahmedabad", pincode: "380001", state: "Gujarat", lat: 23.0225, lng: 72.5714 },
  { city: "Jaipur", pincode: "302001", state: "Rajasthan", lat: 26.9124, lng: 75.7873 },
  { city: "Lucknow", pincode: "226001", state: "Uttar Pradesh", lat: 26.8467, lng: 80.9462 },
  { city: "Chandigarh", pincode: "160001", state: "Chandigarh", lat: 30.7333, lng: 76.7794 },
  { city: "Kochi", pincode: "682001", state: "Kerala", lat: 9.9312, lng: 76.2673 },
  { city: "Indore", pincode: "452001", state: "Madhya Pradesh", lat: 22.7196, lng: 75.8577 },
];

export default function LocationPicker({ 
  currentPincode, 
  currentCity, 
  onLocationChange, 
  isOpen, 
  onClose 
}: LocationPickerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [manualPincode, setManualPincode] = useState('');
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [filteredCities, setFilteredCities] = useState(CITIES);
  const [activeTab, setActiveTab] = useState<'cities' | 'pincode' | 'map'>('cities');
  const [detectingLocation, setDetectingLocation] = useState(false);
  
  // Filter cities based on search
  useEffect(() => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      setFilteredCities(
        CITIES.filter(
          c => c.city.toLowerCase().includes(query) || 
               c.pincode.includes(query) ||
               c.state.toLowerCase().includes(query)
        )
      );
    } else {
      setFilteredCities(CITIES);
    }
  }, [searchQuery]);
  
  // Detect current location using browser geolocation
  const detectLocation = async () => {
    setDetectingLocation(true);
    
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      setDetectingLocation(false);
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        // Find nearest city from our list
        let nearestCity = CITIES[0];
        let minDistance = Infinity;
        
        for (const city of CITIES) {
          const distance = Math.sqrt(
            Math.pow(city.lat - latitude, 2) + 
            Math.pow(city.lng - longitude, 2)
          );
          if (distance < minDistance) {
            minDistance = distance;
            nearestCity = city;
          }
        }
        
        setSelectedLocation(nearestCity);
        setDetectingLocation(false);
      },
      (error) => {
        console.error('Geolocation error:', error);
        alert('Unable to detect location. Please select manually.');
        setDetectingLocation(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };
  
  const handleSelectCity = (location: Location) => {
    setSelectedLocation(location);
  };
  
  const handleConfirm = () => {
    if (activeTab === 'pincode' && manualPincode.length === 6) {
      // Create location from manual pincode
      onLocationChange({
        city: 'Custom',
        pincode: manualPincode,
        state: '',
        lat: 0,
        lng: 0
      });
    } else if (selectedLocation) {
      onLocationChange(selectedLocation);
    }
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <div 
      className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="glass rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-2xl font-bold flex items-center gap-2">
              <span>📍</span> Select Your Location
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <p className="text-gray-400 text-sm">
            Prices vary by location. Select your area for accurate pricing.
          </p>
          
          {/* Current Location */}
          <div className="mt-4 flex items-center gap-2 text-sm">
            <span className="text-gray-500">Current:</span>
            <span className="bg-primary/20 text-primary px-3 py-1 rounded-full">
              {currentCity} - {currentPincode}
            </span>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-white/10">
          <button
            onClick={() => setActiveTab('cities')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'cities' 
                ? 'text-primary border-b-2 border-primary' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🏙️ Select City
          </button>
          <button
            onClick={() => setActiveTab('pincode')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'pincode' 
                ? 'text-primary border-b-2 border-primary' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            📮 Enter Pincode
          </button>
          <button
            onClick={() => setActiveTab('map')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'map' 
                ? 'text-primary border-b-2 border-primary' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🗺️ Map View
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'cities' && (
            <div>
              {/* Detect Location Button */}
              <button
                onClick={detectLocation}
                disabled={detectingLocation}
                className="w-full mb-4 py-3 bg-secondary/20 hover:bg-secondary/30 border border-secondary/30 rounded-xl flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {detectingLocation ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Detecting...
                  </>
                ) : (
                  <>
                    <span>📍</span>
                    Use My Current Location
                  </>
                )}
              </button>
              
              {/* Search */}
              <div className="relative mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search city, area or pincode..."
                  className="w-full px-4 py-3 pl-10 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary/50 transition-colors"
                />
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              
              {/* City List */}
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {filteredCities.map((location) => (
                  <button
                    key={`${location.city}-${location.pincode}`}
                    onClick={() => handleSelectCity(location)}
                    className={`w-full p-4 rounded-xl text-left transition-all ${
                      selectedLocation?.pincode === location.pincode
                        ? 'bg-primary/20 border border-primary/30'
                        : 'glass hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{location.city}</div>
                        <div className="text-sm text-gray-400">
                          {location.state} • {location.pincode}
                        </div>
                      </div>
                      {selectedLocation?.pincode === location.pincode && (
                        <div className="text-primary">
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </button>
                ))}
                
                {filteredCities.length === 0 && (
                  <div className="text-center text-gray-400 py-8">
                    No cities found. Try a different search or enter pincode manually.
                  </div>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'pincode' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Enter 6-digit Pincode</label>
                <input
                  type="text"
                  value={manualPincode}
                  onChange={(e) => setManualPincode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="e.g., 400001"
                  maxLength={6}
                  className="w-full px-6 py-4 text-2xl text-center tracking-[0.5em] bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary/50 transition-colors font-mono"
                />
              </div>
              
              {manualPincode.length === 6 && (
                <div className="bg-primary/10 border border-primary/20 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-primary">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">Valid pincode format</span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">
                    Prices will be shown for pincode: {manualPincode}
                  </p>
                </div>
              )}
              
              {/* Quick Select Popular Pincodes */}
              <div>
                <p className="text-sm text-gray-400 mb-3">Popular Pincodes:</p>
                <div className="flex flex-wrap gap-2">
                  {['400001', '110001', '560001', '500001', '600001', '411001'].map((pin) => (
                    <button
                      key={pin}
                      onClick={() => setManualPincode(pin)}
                      className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                        manualPincode === pin
                          ? 'bg-primary text-white'
                          : 'glass hover:bg-white/10'
                      }`}
                    >
                      {pin}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'map' && (
            <div className="space-y-4">
              {/* Simple India Map with clickable regions */}
              <div className="relative aspect-[4/3] bg-white/5 rounded-xl overflow-hidden">
                {/* SVG Map of India */}
                <svg viewBox="0 0 400 450" className="w-full h-full">
                  {/* Background */}
                  <rect fill="transparent" width="400" height="450" />
                  
                  {/* City markers */}
                  {CITIES.filter((c, i, arr) => 
                    arr.findIndex(x => x.city.split(' - ')[0] === c.city.split(' - ')[0]) === i
                  ).map((city) => {
                    // Normalize coordinates for SVG
                    const x = ((city.lng - 68) / (97 - 68)) * 380 + 10;
                    const y = ((37 - city.lat) / (37 - 8)) * 420 + 15;
                    const isSelected = selectedLocation?.city.split(' - ')[0] === city.city.split(' - ')[0];
                    
                    return (
                      <g key={city.city} onClick={() => handleSelectCity(city)} style={{ cursor: 'pointer' }}>
                        {/* Pulse effect for selected */}
                        {isSelected && (
                          <circle
                            cx={x}
                            cy={y}
                            r="15"
                            fill="rgba(16, 185, 129, 0.3)"
                            className="animate-ping"
                          />
                        )}
                        {/* Marker */}
                        <circle
                          cx={x}
                          cy={y}
                          r={isSelected ? 10 : 6}
                          fill={isSelected ? '#10B981' : '#6366F1'}
                          stroke="white"
                          strokeWidth="2"
                        />
                        {/* Label */}
                        <text
                          x={x}
                          y={y - 12}
                          textAnchor="middle"
                          fill="white"
                          fontSize="10"
                          className="pointer-events-none"
                        >
                          {city.city.split(' - ')[0]}
                        </text>
                      </g>
                    );
                  })}
                </svg>
                
                {/* Legend */}
                <div className="absolute bottom-4 left-4 glass rounded-lg p-3 text-xs">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-3 h-3 rounded-full bg-secondary"></div>
                    <span>Available City</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-primary"></div>
                    <span>Selected</span>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-gray-400 text-center">
                Click on a city marker to select it
              </p>
              
              {selectedLocation && (
                <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 text-center">
                  <div className="font-medium">{selectedLocation.city}</div>
                  <div className="text-sm text-gray-400">{selectedLocation.pincode}</div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t border-white/10">
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-3 glass hover:bg-white/10 rounded-xl font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={activeTab === 'pincode' ? manualPincode.length !== 6 : !selectedLocation}
              className="flex-1 py-3 bg-primary hover:bg-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl font-medium transition-colors"
            >
              Confirm Location
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

