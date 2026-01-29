"""Data models for PropStream property data."""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional, List
from datetime import datetime


@dataclass
class Address:
    """Property address information."""
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    county: str = ""
    full_address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    apn: str = ""
    subdivision: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Address":
        """Create Address from PropStream API response."""
        # PropStream nests address in an 'address' dict
        addr = data.get("address", {}) if isinstance(data.get("address"), dict) else {}
        
        return cls(
            street=addr.get("streetAddress", addr.get("baseStreetAddress", "")),
            city=addr.get("cityName", data.get("jurisdiction", "")),
            state=addr.get("stateCode", ""),
            zip_code=str(addr.get("zip", "")),
            county=addr.get("countyName", data.get("countyName", "")),
            full_address=addr.get("label", addr.get("title", "")),
            latitude=_safe_float(data.get("latitude")),
            longitude=_safe_float(data.get("longitude")),
            apn=data.get("apn", ""),
            subdivision=data.get("subdivision", ""),
        )


@dataclass
class Owner:
    """Property owner information."""
    name: str = ""
    owner1_full_name: str = ""
    owner2_full_name: str = ""
    mailing_address: str = ""
    mailing_city: str = ""
    mailing_state: str = ""
    mailing_zip: str = ""
    mailing_care_of: str = ""
    owner_type: str = ""  # Individual, Corporation, Trust, etc.
    ownership_type: str = ""  # Community Property, etc.
    is_absentee: bool = False
    is_owner_occupied: bool = False
    ownership_length_months: Optional[int] = None
    properties_owned: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Create Owner from PropStream API response."""
        # PropStream nests mail address in 'mailAddress' dict
        mail = data.get("mailAddress", {}) if isinstance(data.get("mailAddress"), dict) else {}
        
        # Determine if absentee (not owner occupied)
        is_owner_occupied = data.get("ownerOccupied", False)
        
        return cls(
            name=data.get("ownerNames", data.get("effectiveOwner1FullName", "")),
            owner1_full_name=data.get("owner1FullName", data.get("effectiveOwner1FullName", "")),
            owner2_full_name=data.get("owner2FullName", data.get("effectiveOwner2FullName", "")),
            mailing_address=mail.get("streetAddress", ""),
            mailing_city=mail.get("city", ""),
            mailing_state=mail.get("state", ""),
            mailing_zip=str(mail.get("zip", "")),
            mailing_care_of=data.get("mailCareOf", ""),
            owner_type=data.get("ownerType", ""),
            ownership_type=data.get("ownerOwnershipType", data.get("ownership", "")),
            is_absentee=not is_owner_occupied,
            is_owner_occupied=is_owner_occupied,
            ownership_length_months=_safe_int(data.get("ownershipLength")),
            properties_owned=_safe_int(data.get("propertiesOwned")),
        )


@dataclass
class PropertyDetails:
    """Physical property details."""
    property_type: str = ""  # Single Family, Multi-Family, Condo, etc.
    property_class: str = ""  # Residential, Commercial, etc.
    land_use: str = ""
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    full_bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    building_sqft: Optional[int] = None
    lot_size_sqft: Optional[int] = None
    lot_size_acres: Optional[float] = None
    year_built: Optional[int] = None
    age: Optional[int] = None
    stories: Optional[float] = None
    parking_spaces: Optional[int] = None
    pool: bool = False
    pool_type: str = ""
    exterior_wall: str = ""
    roof_type: str = ""
    heating_type: str = ""
    ac_type: str = ""
    hoa_name: str = ""
    hoa_fee: Optional[float] = None
    hoa_fee_frequency: str = ""
    hoa_annual_total: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PropertyDetails":
        """Create PropertyDetails from PropStream API response."""
        return cls(
            property_type=data.get("propertyType", ""),
            property_class=data.get("propertyClass", ""),
            land_use=data.get("landUse", ""),
            bedrooms=_safe_int(data.get("bedrooms")),
            bathrooms=_safe_float(data.get("bathrooms")),
            full_bathrooms=_safe_int(data.get("fullBathrooms")),
            sqft=_safe_int(data.get("livingSquareFeet", data.get("squareFeet"))),
            building_sqft=_safe_int(data.get("buildingSquareFeet")),
            lot_size_sqft=_safe_int(data.get("lotSquareFeet")),
            lot_size_acres=_safe_float(data.get("lotAcres")),
            year_built=_safe_int(data.get("yearBuilt", data.get("effectiveYearBuilt"))),
            age=_safe_int(data.get("age")),
            stories=_safe_float(data.get("stories")),
            parking_spaces=_safe_int(data.get("parkingSpaces")),
            pool=data.get("poolAvailable", False),
            pool_type=data.get("poolType", ""),
            exterior_wall=data.get("exteriorWallType", ""),
            roof_type=data.get("roofCoverType", ""),
            heating_type=data.get("heatingType", ""),
            ac_type=data.get("airConditioningType", ""),
            hoa_name=data.get("hoa1Name", ""),
            hoa_fee=_safe_float(data.get("hoa1Fee")),
            hoa_fee_frequency=data.get("hoa1FeeFrequency", ""),
            hoa_annual_total=_safe_float(data.get("hoaFeeAnnualTotal")),
        )


@dataclass
class Valuation:
    """Property valuation estimates."""
    estimated_value: Optional[int] = None
    estimated_equity: Optional[int] = None
    equity_percentage: Optional[float] = None
    assessed_value: Optional[int] = None
    market_value: Optional[int] = None
    market_land_value: Optional[int] = None
    market_improvement_value: Optional[int] = None
    last_sale_price: Optional[int] = None
    last_sale_date: Optional[str] = None
    price_per_sqft: Optional[float] = None
    comp_sale_amount: Optional[int] = None
    comp_days_on_market: Optional[int] = None
    rent_estimate: Optional[int] = None
    gross_yield: Optional[float] = None
    ltv_ratio: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Valuation":
        """Create Valuation from PropStream API response."""
        # Convert timestamp to date string if needed
        last_sale_ts = data.get("lastSaleDate", data.get("effectiveLastSaleDate"))
        last_sale_date = None
        if last_sale_ts and isinstance(last_sale_ts, (int, float)):
            from datetime import datetime
            try:
                last_sale_date = datetime.fromtimestamp(last_sale_ts / 1000).strftime("%Y-%m-%d")
            except:
                last_sale_date = str(last_sale_ts)
        
        return cls(
            estimated_value=_safe_int(data.get("estimatedValue")),
            estimated_equity=_safe_int(data.get("estimatedEquity")),
            equity_percentage=_safe_float(data.get("equityPercentage")),
            assessed_value=_safe_int(data.get("assessedValue")),
            market_value=_safe_int(data.get("marketValue")),
            market_land_value=_safe_int(data.get("marketLandValue")),
            market_improvement_value=_safe_int(data.get("marketImprovementValue")),
            last_sale_price=_safe_int(data.get("lastSaleAmount")),
            last_sale_date=last_sale_date,
            price_per_sqft=_safe_float(data.get("pricePerSquareFoot")),
            comp_sale_amount=_safe_int(data.get("compSaleAmount")),
            comp_days_on_market=_safe_int(data.get("compDaysOnMarket")),
            rent_estimate=_safe_int(data.get("rentAmount")),
            gross_yield=_safe_float(data.get("grossYield")),
            ltv_ratio=_safe_float(data.get("ltvRatio")),
        )


@dataclass
class TaxInfo:
    """Property tax information."""
    annual_tax: Optional[float] = None
    tax_year: Optional[int] = None
    assessment_year: Optional[int] = None
    tax_delinquent: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "TaxInfo":
        """Create TaxInfo from PropStream API response."""
        return cls(
            annual_tax=_safe_float(data.get("taxAmount")),
            tax_year=_safe_int(data.get("taxYear")),
            assessment_year=_safe_int(data.get("assessmentYear")),
            tax_delinquent=False,  # Would need to check distress flags
        )


@dataclass
class MortgageInfo:
    """Mortgage/lien information."""
    has_mortgage: bool = False
    mortgage_balance: Optional[int] = None
    open_mortgage_count: Optional[int] = None
    open_lien_amount: Optional[int] = None
    open_lien_count: Optional[int] = None
    purchase_method: str = ""  # Financed, Cash, etc.

    @classmethod
    def from_dict(cls, data: dict) -> "MortgageInfo":
        """Create MortgageInfo from PropStream API response."""
        open_mortgages = _safe_int(data.get("openMortgageQuantity", 0))
        
        return cls(
            has_mortgage=open_mortgages > 0 if open_mortgages else False,
            mortgage_balance=_safe_int(data.get("mortgageBalance", data.get("openMortgageBalance"))),
            open_mortgage_count=open_mortgages,
            open_lien_amount=_safe_int(data.get("openLienAmount")),
            open_lien_count=_safe_int(data.get("openLiens", data.get("lienCount"))),
            purchase_method=data.get("purchaseMethod", ""),
        )


@dataclass
class DistressInfo:
    """Distress/foreclosure information."""
    is_distressed: bool = False
    distress_status: str = ""  # Pre-Foreclosure, Foreclosure, etc.
    market_status: str = ""  # On Market, Off Market, etc.

    @classmethod
    def from_dict(cls, data: dict) -> "DistressInfo":
        """Create DistressInfo from PropStream API response."""
        return cls(
            is_distressed=data.get("distressed", False),
            distress_status=data.get("distressStatus", ""),
            market_status=data.get("marketStatus", ""),
        )


@dataclass
class Property:
    """Complete property record."""
    id: str = ""
    apn: str = ""  # Assessor's Parcel Number
    address: Address = field(default_factory=Address)
    owner: Owner = field(default_factory=Owner)
    details: PropertyDetails = field(default_factory=PropertyDetails)
    valuation: Valuation = field(default_factory=Valuation)
    tax_info: TaxInfo = field(default_factory=TaxInfo)
    mortgage: MortgageInfo = field(default_factory=MortgageInfo)
    distress: DistressInfo = field(default_factory=DistressInfo)
    raw_data: dict = field(default_factory=dict)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> "Property":
        """
        Create Property from PropStream API response dictionary.
        
        PropStream returns flat property data with all fields at top level.
        """
        return cls(
            id=str(data.get("id", data.get("propertyId", ""))),
            apn=str(data.get("apn", "")),
            address=Address.from_dict(data),
            owner=Owner.from_dict(data),
            details=PropertyDetails.from_dict(data),
            valuation=Valuation.from_dict(data),
            tax_info=TaxInfo.from_dict(data),
            mortgage=MortgageInfo.from_dict(data),
            distress=DistressInfo.from_dict(data),
            raw_data=data,
        )

    def to_dict(self) -> dict:
        """Convert Property to dictionary."""
        return asdict(self)

    def to_flat_dict(self) -> dict:
        """
        Flatten the property to a single-level dictionary.
        Useful for CSV export.
        """
        return {
            "id": self.id,
            "apn": self.apn,
            "fetched_at": self.fetched_at,
            # Address
            "street": self.address.street,
            "city": self.address.city,
            "state": self.address.state,
            "zip_code": self.address.zip_code,
            "county": self.address.county,
            "subdivision": self.address.subdivision,
            "latitude": self.address.latitude,
            "longitude": self.address.longitude,
            # Owner
            "owner_name": self.owner.name,
            "owner1_full_name": self.owner.owner1_full_name,
            "owner2_full_name": self.owner.owner2_full_name,
            "owner_mailing_address": self.owner.mailing_address,
            "owner_mailing_city": self.owner.mailing_city,
            "owner_mailing_state": self.owner.mailing_state,
            "owner_mailing_zip": self.owner.mailing_zip,
            "owner_type": self.owner.owner_type,
            "ownership_type": self.owner.ownership_type,
            "is_absentee": self.owner.is_absentee,
            "is_owner_occupied": self.owner.is_owner_occupied,
            "ownership_length_months": self.owner.ownership_length_months,
            "properties_owned": self.owner.properties_owned,
            # Details
            "property_type": self.details.property_type,
            "property_class": self.details.property_class,
            "land_use": self.details.land_use,
            "bedrooms": self.details.bedrooms,
            "bathrooms": self.details.bathrooms,
            "sqft": self.details.sqft,
            "lot_size_sqft": self.details.lot_size_sqft,
            "lot_size_acres": self.details.lot_size_acres,
            "year_built": self.details.year_built,
            "age": self.details.age,
            "stories": self.details.stories,
            "parking_spaces": self.details.parking_spaces,
            "pool": self.details.pool,
            "pool_type": self.details.pool_type,
            "roof_type": self.details.roof_type,
            "heating_type": self.details.heating_type,
            "ac_type": self.details.ac_type,
            "hoa_name": self.details.hoa_name,
            "hoa_fee": self.details.hoa_fee,
            "hoa_annual_total": self.details.hoa_annual_total,
            # Valuation
            "estimated_value": self.valuation.estimated_value,
            "estimated_equity": self.valuation.estimated_equity,
            "equity_percentage": self.valuation.equity_percentage,
            "assessed_value": self.valuation.assessed_value,
            "market_value": self.valuation.market_value,
            "last_sale_price": self.valuation.last_sale_price,
            "last_sale_date": self.valuation.last_sale_date,
            "price_per_sqft": self.valuation.price_per_sqft,
            "rent_estimate": self.valuation.rent_estimate,
            "gross_yield": self.valuation.gross_yield,
            "ltv_ratio": self.valuation.ltv_ratio,
            # Tax
            "annual_tax": self.tax_info.annual_tax,
            "tax_year": self.tax_info.tax_year,
            # Mortgage
            "has_mortgage": self.mortgage.has_mortgage,
            "mortgage_balance": self.mortgage.mortgage_balance,
            "open_mortgage_count": self.mortgage.open_mortgage_count,
            "open_lien_amount": self.mortgage.open_lien_amount,
            "open_lien_count": self.mortgage.open_lien_count,
            "purchase_method": self.mortgage.purchase_method,
            # Distress
            "is_distressed": self.distress.is_distressed,
            "distress_status": self.distress.distress_status,
            "market_status": self.distress.market_status,
        }


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert a value to int."""
    if value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_properties(data: dict) -> List[Property]:
    """
    Parse a list of properties from PropStream API response.
    
    PropStream returns:
    - {"properties": [...], "neighbors": [...], ...} for property lookup
    - {"results": [...]} or similar for searches
    """
    # Find the list of properties in the response
    properties_list = None
    
    if isinstance(data, list):
        properties_list = data
    elif isinstance(data, dict):
        # PropStream uses 'properties' key for main results
        for key in ["properties", "results", "data", "records", "items"]:
            if key in data and isinstance(data[key], list):
                properties_list = data[key]
                break
    
    if properties_list is None:
        # Single property response
        if isinstance(data, dict) and ("id" in data or "apn" in data or "propertyId" in data):
            return [Property.from_dict(data)]
        return []
    
    return [Property.from_dict(p) for p in properties_list]
