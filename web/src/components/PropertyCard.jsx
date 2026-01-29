function PropertyCard({ property }) {
  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleDateString()
  }

  const address = property.address || {}
  const equityPercent = property.equityPercentage || 0
  const isNegativeEquity = property.estimatedEquity < 0

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      {/* Header with Address */}
      <div className="bg-gradient-to-r from-orange-600 to-orange-700 px-6 py-4">
        <h2 className="text-2xl font-bold text-white">
          {address.streetAddress || 'Unknown Address'}
        </h2>
        <p className="text-orange-100">
          {address.cityName}, {address.stateCode} {address.zip} • {property.countyName} County
        </p>
        <p className="text-orange-200 text-sm mt-1">
          APN: {property.apn}
        </p>
      </div>

      {/* Key Stats Grid */}
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {/* Estimated Value */}
          <StatBox
            label="Est. Value"
            value={formatCurrency(property.estimatedValue)}
            color="text-green-400"
          />
          
          {/* Equity */}
          <StatBox
            label="Equity"
            value={formatCurrency(Math.abs(property.estimatedEquity))}
            subtext={`${equityPercent}%`}
            color={isNegativeEquity ? 'text-red-400' : 'text-green-400'}
            prefix={isNegativeEquity ? '-' : '+'}
          />
          
          {/* Mortgage Balance */}
          <StatBox
            label="Mortgage Bal."
            value={formatCurrency(property.mortgageBalance)}
            color="text-yellow-400"
          />
          
          {/* Last Sale */}
          <StatBox
            label="Last Sale"
            value={formatCurrency(property.lastSaleAmount)}
            subtext={formatDate(property.lastSaleDate)}
            color="text-blue-400"
          />
          
          {/* Property Type */}
          <StatBox
            label="Type"
            value={property.propertyType || 'N/A'}
            color="text-purple-400"
          />
          
          {/* Owner */}
          <StatBox
            label="Owner"
            value={property.ownerNames || property.owner1FullName || 'N/A'}
            subtext={property.ownerOccupied ? 'Owner Occupied' : 'Absentee'}
            color="text-cyan-400"
            small
          />
        </div>

        {/* Second Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mt-4">
          <MiniStat label="Beds" value={property.bedrooms || '?'} />
          <MiniStat label="Baths" value={property.bathrooms || '?'} />
          <MiniStat label="Sqft" value={property.squareFeet?.toLocaleString() || '?'} />
          <MiniStat label="Lot" value={`${property.lotAcres || '?'} ac`} />
          <MiniStat label="Year" value={property.yearBuilt || '?'} />
          <MiniStat label="Stories" value={property.stories || '?'} />
          <MiniStat label="Tax/Yr" value={formatCurrency(property.taxAmount)} />
          <MiniStat label="Rent Est." value={formatCurrency(property.rentAmount)} />
        </div>

        {/* Status Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          {property.distressed && (
            <Badge color="red">Distressed</Badge>
          )}
          {property.distressStatus && property.distressStatus !== 'No' && (
            <Badge color="red">{property.distressStatus}</Badge>
          )}
          {property.ownerOccupied && (
            <Badge color="green">Owner Occupied</Badge>
          )}
          {!property.ownerOccupied && (
            <Badge color="yellow">Absentee Owner</Badge>
          )}
          {property.marketStatus && (
            <Badge color="blue">{property.marketStatus}</Badge>
          )}
          {property.equity && (
            <Badge color="green">High Equity</Badge>
          )}
          {property.openLiens > 0 && (
            <Badge color="orange">{property.openLiens} Open Liens</Badge>
          )}
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value, subtext, color, prefix, small }) {
  return (
    <div className="bg-gray-700/50 rounded-lg p-3">
      <p className="text-gray-400 text-xs uppercase tracking-wide">{label}</p>
      <p className={`${color} ${small ? 'text-sm' : 'text-xl'} font-bold truncate`}>
        {prefix}{value}
      </p>
      {subtext && (
        <p className="text-gray-500 text-xs truncate">{subtext}</p>
      )}
    </div>
  )
}

function MiniStat({ label, value }) {
  return (
    <div className="text-center">
      <p className="text-gray-400 text-xs">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  )
}

function Badge({ children, color }) {
  const colors = {
    red: 'bg-red-900/50 text-red-300 border-red-700',
    green: 'bg-green-900/50 text-green-300 border-green-700',
    yellow: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
    blue: 'bg-blue-900/50 text-blue-300 border-blue-700',
    orange: 'bg-orange-900/50 text-orange-300 border-orange-700',
  }
  
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded border ${colors[color]}`}>
      {children}
    </span>
  )
}

export default PropertyCard
