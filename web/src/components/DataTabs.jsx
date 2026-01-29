import { useState } from 'react'

function DataTabs({ data }) {
  const [activeTab, setActiveTab] = useState('all')
  
  const property = data.properties?.[0] || {}
  
  const tabs = [
    { id: 'all', label: 'All Fields', count: Object.keys(property).length },
    { id: 'owner', label: 'Owner', icon: '👤' },
    { id: 'property', label: 'Property', icon: '🏠' },
    { id: 'value', label: 'Valuation', icon: '💰' },
    { id: 'mortgage', label: 'Mortgage', icon: '🏦' },
    { id: 'sales', label: 'Sale History', count: property.sales?.length || 0 },
    { id: 'taxes', label: 'Tax History', count: property.taxes?.length || 0 },
    { id: 'neighbors', label: 'Neighbors', count: data.neighbors?.length || 0 },
    { id: 'mls', label: 'MLS Listings', count: data.nearbyMlsListings?.length || 0 },
    { id: 'preforeclosure', label: 'Pre-Foreclosures', count: data.nearbyPreForeclosures?.length || 0 },
    { id: 'foreclosure', label: 'Foreclosures', count: data.nearbyForeclosures?.length || 0 },
  ]

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      {/* Tab Navigation */}
      <div className="border-b border-gray-700 overflow-x-auto">
        <div className="flex min-w-max">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-gray-700 text-orange-400 border-b-2 border-orange-500'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              {tab.icon && <span className="mr-1">{tab.icon}</span>}
              {tab.label}
              {tab.count !== undefined && (
                <span className="ml-1 text-xs text-gray-500">({tab.count})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4 max-h-[600px] overflow-auto">
        {activeTab === 'all' && <AllFieldsTab property={property} />}
        {activeTab === 'owner' && <OwnerTab property={property} />}
        {activeTab === 'property' && <PropertyTab property={property} />}
        {activeTab === 'value' && <ValuationTab property={property} />}
        {activeTab === 'mortgage' && <MortgageTab property={property} />}
        {activeTab === 'sales' && <SalesTab sales={property.sales} lastSale={property.lastSale} />}
        {activeTab === 'taxes' && <TaxesTab taxes={property.taxes} />}
        {activeTab === 'neighbors' && <PropertiesTable data={data.neighbors} title="Neighbors" />}
        {activeTab === 'mls' && <PropertiesTable data={data.nearbyMlsListings} title="MLS Listings" />}
        {activeTab === 'preforeclosure' && <PropertiesTable data={data.nearbyPreForeclosures} title="Pre-Foreclosures" />}
        {activeTab === 'foreclosure' && <PropertiesTable data={data.nearbyForeclosures} title="Foreclosures" />}
      </div>
    </div>
  )
}

function AllFieldsTab({ property }) {
  const formatValue = (value) => {
    if (value === null || value === undefined) return <span className="text-gray-500">null</span>
    if (typeof value === 'boolean') return <span className={value ? 'text-green-400' : 'text-red-400'}>{value.toString()}</span>
    if (typeof value === 'object') return <span className="text-blue-400">{JSON.stringify(value).slice(0, 100)}...</span>
    if (typeof value === 'number') return <span className="text-yellow-400">{value.toLocaleString()}</span>
    return <span className="text-white">{String(value)}</span>
  }

  const sortedKeys = Object.keys(property).sort()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
      {sortedKeys.map(key => (
        <div key={key} className="flex gap-2 py-1 border-b border-gray-700/50">
          <span className="text-gray-400 font-mono text-sm min-w-[200px]">{key}:</span>
          <span className="text-sm truncate">{formatValue(property[key])}</span>
        </div>
      ))}
    </div>
  )
}

function OwnerTab({ property }) {
  const fields = [
    ['Owner Name', property.ownerNames || property.owner1FullName],
    ['Owner 1', property.owner1FullName],
    ['Owner 2', property.owner2FullName],
    ['Owner Type', property.ownerType],
    ['Ownership', property.ownership],
    ['Occupancy', property.ownerOccupancy],
    ['Owner Occupied', property.ownerOccupied ? 'Yes' : 'No'],
    ['Ownership Length', `${property.ownershipLength} months`],
    ['Properties Owned', property.propertiesOwned],
    ['Mail Care Of', property.mailCareOf],
  ]

  const mailAddr = property.mailAddress || {}

  return (
    <div className="space-y-6">
      <FieldsGrid fields={fields} />
      
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Mailing Address</h3>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <p className="text-white">{mailAddr.streetAddress}</p>
          <p className="text-gray-400">{mailAddr.cityName}, {mailAddr.stateCode} {mailAddr.zip}</p>
        </div>
      </div>
    </div>
  )
}

function PropertyTab({ property }) {
  const fields = [
    ['Property Type', property.propertyType],
    ['Property Class', property.propertyClass],
    ['Land Use', property.landUse],
    ['Living Sqft', property.livingSquareFeet?.toLocaleString()],
    ['Building Sqft', property.buildingSquareFeet?.toLocaleString()],
    ['Gross Sqft', property.grossSquareFeet?.toLocaleString()],
    ['Lot Sqft', property.lotSquareFeet?.toLocaleString()],
    ['Lot Acres', property.lotAcres],
    ['Bedrooms', property.bedrooms],
    ['Bathrooms', property.bathrooms],
    ['Full Baths', property.fullBathrooms],
    ['Stories', property.stories],
    ['Year Built', property.yearBuilt],
    ['Age', property.age],
    ['Parking Spaces', property.parkingSpaces],
    ['Garage Type', property.garageType],
    ['Pool', property.poolAvailable ? 'Yes' : 'No'],
    ['Construction', property.buildingConstructionType],
    ['Exterior Wall', property.exteriorWallType],
    ['Roof', property.roofCoverType],
    ['Heating', property.heatingType],
    ['A/C', property.airConditioningType],
    ['Condition', property.buildingCondition],
    ['Quality', property.constructionQuality],
    ['Zoning', property.zoning],
    ['Subdivision', property.subdivision],
    ['School District', property.schoolDistrict],
    ['Legal Description', property.legalDescription],
  ]

  return <FieldsGrid fields={fields} />
}

function ValuationTab({ property }) {
  const formatCurrency = (v) => v ? `$${v.toLocaleString()}` : 'N/A'
  
  const fields = [
    ['Estimated Value', formatCurrency(property.estimatedValue)],
    ['Estimated Equity', formatCurrency(property.estimatedEquity)],
    ['Equity %', `${property.equityPercentage}%`],
    ['Market Value', formatCurrency(property.marketValue)],
    ['Market Land Value', formatCurrency(property.marketLandValue)],
    ['Market Improvement Value', formatCurrency(property.marketImprovementValue)],
    ['Assessed Value', formatCurrency(property.assessedValue)],
    ['Assessment Year', property.assessmentYear],
    ['Price/Sqft', `$${property.pricePerSquareFoot}`],
    ['LTV Ratio', `${((property.ltvRatio || 0) * 100).toFixed(1)}%`],
    ['Rent Estimate', formatCurrency(property.rentAmount)],
    ['Gross Yield', `${((property.grossYield || 0) * 100).toFixed(2)}%`],
    ['Comp Sale Amount', formatCurrency(property.compSaleAmount)],
    ['Comp Days on Market', property.compDaysOnMarket],
    ['Comps Count', property.comps],
  ]

  return <FieldsGrid fields={fields} />
}

function MortgageTab({ property }) {
  const formatCurrency = (v) => v ? `$${v.toLocaleString()}` : 'N/A'
  
  const fields = [
    ['Mortgage Balance', formatCurrency(property.mortgageBalance)],
    ['Open Mortgage Balance', formatCurrency(property.openMortgageBalance)],
    ['Open Mortgages', property.openMortgageQuantity],
    ['Open Liens', property.openLiens],
    ['Open Lien Amount', formatCurrency(property.openLienAmount)],
    ['Lien Count', property.lienCount],
    ['Purchase Method', property.purchaseMethod],
  ]

  return (
    <div className="space-y-6">
      <FieldsGrid fields={fields} />
      
      {property.mortgages && property.mortgages.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">Mortgage Records ({property.mortgages.length})</h3>
          <div className="space-y-2">
            {property.mortgages.map((m, i) => (
              <div key={i} className="bg-gray-700/50 rounded-lg p-3">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                  <div>
                    <span className="text-gray-400">Amount:</span>
                    <span className="text-white ml-2">{formatCurrency(m.amount)}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Rate:</span>
                    <span className="text-white ml-2">{m.interestRate ? `${(m.interestRate * 100).toFixed(2)}%` : 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Lender:</span>
                    <span className="text-white ml-2">{m.lenderName || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Date:</span>
                    <span className="text-white ml-2">{m.recordingDate ? new Date(m.recordingDate).toLocaleDateString() : 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function SalesTab({ sales, lastSale }) {
  const formatCurrency = (v) => v ? `$${v.toLocaleString()}` : 'N/A'
  
  return (
    <div className="space-y-4">
      {lastSale && (
        <div className="bg-orange-900/30 border border-orange-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-orange-400 mb-2">Last Sale Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div><span className="text-gray-400">Sale Amount:</span> <span className="text-white">{formatCurrency(lastSale.saleAmount)}</span></div>
            <div><span className="text-gray-400">Date:</span> <span className="text-white">{lastSale.saleDate ? new Date(lastSale.saleDate).toLocaleDateString() : 'N/A'}</span></div>
            <div><span className="text-gray-400">Document:</span> <span className="text-white">{lastSale.documentNumber}</span></div>
            <div><span className="text-gray-400">Type:</span> <span className="text-white">{lastSale.documentType}</span></div>
            <div><span className="text-gray-400">Seller:</span> <span className="text-white">{lastSale.seller1FullName}</span></div>
            <div><span className="text-gray-400">Buyer:</span> <span className="text-white">{lastSale.owner1FullName}</span></div>
            <div><span className="text-gray-400">Title Company:</span> <span className="text-white">{lastSale.titleCompany}</span></div>
            <div><span className="text-gray-400">Mortgage Amount:</span> <span className="text-white">{formatCurrency(lastSale.mortgage1Amount)}</span></div>
            <div><span className="text-gray-400">Lender:</span> <span className="text-white">{lastSale.mortgage1LenderName}</span></div>
          </div>
        </div>
      )}
      
      {sales && sales.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">All Sales ({sales.length})</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2 text-gray-400">Date</th>
                <th className="text-left py-2 text-gray-400">Amount</th>
                <th className="text-left py-2 text-gray-400">Document</th>
                <th className="text-left py-2 text-gray-400">Mortgage</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale, i) => (
                <tr key={i} className="border-b border-gray-700/50">
                  <td className="py-2 text-white">{sale.saleDate ? new Date(sale.saleDate).toLocaleDateString() : new Date(sale.recordingDate).toLocaleDateString()}</td>
                  <td className="py-2 text-green-400">{formatCurrency(sale.saleAmount)}</td>
                  <td className="py-2 text-gray-400">{sale.documentNumber}</td>
                  <td className="py-2 text-yellow-400">{formatCurrency(sale.mortgage1Amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function TaxesTab({ taxes }) {
  if (!taxes || taxes.length === 0) {
    return <p className="text-gray-400">No tax history available</p>
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-gray-700">
          <th className="text-left py-2 text-gray-400">Year</th>
          <th className="text-left py-2 text-gray-400">Tax Amount</th>
          <th className="text-left py-2 text-gray-400">Assessed Value</th>
          <th className="text-left py-2 text-gray-400">Change</th>
        </tr>
      </thead>
      <tbody>
        {taxes.map((tax, i) => (
          <tr key={i} className="border-b border-gray-700/50">
            <td className="py-2 text-white">{tax.year}</td>
            <td className="py-2 text-green-400">${tax.taxAmount?.toLocaleString()}</td>
            <td className="py-2 text-blue-400">${tax.assessedValue?.toLocaleString()}</td>
            <td className={`py-2 ${tax.taxAmountChange > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {tax.taxAmountChange ? `${tax.taxAmountChange > 0 ? '+' : ''}${tax.taxAmountChange.toFixed(1)}%` : '-'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function PropertiesTable({ data, title }) {
  if (!data || data.length === 0) {
    return <p className="text-gray-400">No {title.toLowerCase()} data available</p>
  }

  const formatCurrency = (v) => v ? `$${v.toLocaleString()}` : '-'

  return (
    <div>
      <p className="text-gray-400 mb-2">{data.length} properties</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-2 text-gray-400 min-w-[200px]">Address</th>
              <th className="text-left py-2 text-gray-400">Type</th>
              <th className="text-left py-2 text-gray-400">Beds</th>
              <th className="text-left py-2 text-gray-400">Baths</th>
              <th className="text-left py-2 text-gray-400">Sqft</th>
              <th className="text-left py-2 text-gray-400">Year</th>
              <th className="text-left py-2 text-gray-400">Est. Value</th>
              <th className="text-left py-2 text-gray-400">Equity</th>
              <th className="text-left py-2 text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 50).map((p, i) => (
              <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                <td className="py-2 text-white">{p.streetAddress || p.address?.streetAddress || '-'}</td>
                <td className="py-2 text-gray-400">{p.type || p.propertyType || '-'}</td>
                <td className="py-2 text-white">{p.bedrooms || '-'}</td>
                <td className="py-2 text-white">{p.bathrooms || '-'}</td>
                <td className="py-2 text-white">{p.squareFeet?.toLocaleString() || '-'}</td>
                <td className="py-2 text-white">{p.yearBuilt || '-'}</td>
                <td className="py-2 text-green-400">{formatCurrency(p.estimatedValue)}</td>
                <td className={`py-2 ${p.estimatedEquity < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {formatCurrency(p.estimatedEquity)}
                </td>
                <td className="py-2">
                  {p.status && <span className="text-orange-400">{p.status}</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.length > 50 && (
          <p className="text-gray-500 text-center py-2">Showing 50 of {data.length}</p>
        )}
      </div>
    </div>
  )
}

function FieldsGrid({ fields }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {fields.map(([label, value], i) => (
        <div key={i} className="bg-gray-700/50 rounded px-3 py-2">
          <span className="text-gray-400 text-sm">{label}:</span>
          <span className="text-white ml-2">{value || 'N/A'}</span>
        </div>
      ))}
    </div>
  )
}

export default DataTabs
