import { useState } from 'react'
import SearchBar from './components/SearchBar'
import PropertyCard from './components/PropertyCard'
import DataTabs from './components/DataTabs'
import Stats from './components/Stats'

function App() {
  const [propertyData, setPropertyData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (address) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/lookup?address=${encodeURIComponent(address)}`)
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
        setPropertyData(null)
      } else {
        setPropertyData(data)
        setError(null)
      }
    } catch (err) {
      setError('Failed to connect to API. Make sure the Flask server is running.')
      setPropertyData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-orange-500">
              PropStream Explorer
            </h1>
            <Stats />
          </div>
          <div className="mt-4">
            <SearchBar onSearch={handleSearch} loading={loading} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
            <span className="ml-4 text-gray-400">Searching PropStream...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Results */}
        {propertyData && !loading && (
          <div className="space-y-6">
            {/* Main Property Card */}
            {propertyData.properties && propertyData.properties[0] && (
              <PropertyCard property={propertyData.properties[0]} />
            )}

            {/* Tabbed Data */}
            <DataTabs data={propertyData} />
          </div>
        )}

        {/* Empty State */}
        {!propertyData && !loading && !error && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🏠</div>
            <h2 className="text-2xl font-semibold text-gray-400 mb-2">
              Search for a Property
            </h2>
            <p className="text-gray-500">
              Enter an address above to see all PropStream data
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
