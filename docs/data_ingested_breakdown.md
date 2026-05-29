# Data Ingested Breakdown

This document explains what data WOOTD ingests, why it matters for the product, and which providers could be added later.

## Business Case

WOOTD answers a simple user question:

```text
What should I wear today?
```

To answer that, the platform needs weather signals that directly affect clothing decisions:

```text
temperature
rain probability
wind
UV index
weather condition
forecast date
city
```

The ingestion layer stores raw provider responses in Snowflake. dbt then transforms that raw data into clean forecast tables for the API.

## Current Providers

### Open-Meteo

Open-Meteo is the primary global weather provider.

Destination table:

```text
RAW.OPEN_METEO_FORECASTS
```

Raw table shape:

```text
INGESTION_ID
PROVIDER
CITY_NAME
LATITUDE
LONGITUDE
INGESTED_AT
PAYLOAD
```

Important payload fields:

```text
payload:daily:time
payload:daily:temperature_2m_min
payload:daily:temperature_2m_max
payload:daily:precipitation_probability_max
payload:daily:wind_speed_10m_max
payload:daily:uv_index_max
```

Business value:

| Field | Meaning | Outfit Decision |
|---|---|---|
| `temperature_2m_min` | Daily low temperature | Morning cold risk, layering |
| `temperature_2m_max` | Daily high temperature | Afternoon heat risk |
| `precipitation_probability_max` | Highest rain probability | Umbrella, raincoat, waterproof shoes |
| `wind_speed_10m_max` | Maximum wind speed | Windbreaker or heavier outer layer |
| `uv_index_max` | Maximum UV exposure | Sunglasses, sunscreen, hat |
| `time` | Forecast date | Recommendation date |

Example:

```text
temp_min_c = 10
temp_max_c = 18
precip_probability = 0.60
wind_kmh = 20
uv_index = 4
```

Possible recommendation:

```text
long-sleeve shirt
light jacket
compact umbrella
```

### NOAA

NOAA is a secondary provider for US cities.

Destination table:

```text
RAW.NOAA_FORECASTS
```

Raw table shape:

```text
INGESTION_ID
PROVIDER
CITY_NAME
INGESTED_AT
PAYLOAD
```

Important payload fields:

```text
payload:properties:periods
payload:properties:periods[].startTime
payload:properties:periods[].endTime
payload:properties:periods[].temperature
payload:properties:periods[].temperatureUnit
payload:properties:periods[].probabilityOfPrecipitation
payload:properties:periods[].windSpeed
payload:properties:periods[].shortForecast
payload:properties:periods[].isDaytime
```

Business value:

| Field | Meaning | Outfit Decision |
|---|---|---|
| `temperature` | Period temperature | Clothing warmth |
| `temperatureUnit` | Unit metadata | Convert Fahrenheit to Celsius |
| `probabilityOfPrecipitation` | Rain probability | Umbrella or rain layer |
| `windSpeed` | Wind text | Windbreaker decision |
| `shortForecast` | Human-readable condition | User explanation |
| `isDaytime` | Day/night marker | Daytime outfit relevance |

NOAA currently adds value mainly for New York because the default city list includes New York and the NOAA city map supports it.

## Why Store Raw JSON?

The RAW layer is intentionally not cleaned or flattened.

Benefits:

- preserves original API responses
- supports replay if dbt logic changes
- helps debug provider/API changes
- separates extraction from transformation
- gives an audit trail for interviews and production reasoning

Bad pattern:

```text
Python fetches API
Python cleans all data
Python applies business logic
Python writes final tables
```

Better pattern used here:

```text
Python fetches API
Python writes raw JSON to Snowflake
dbt parses and transforms
API reads clean marts
```

## How Raw Data Becomes Business Data

```text
RAW.OPEN_METEO_FORECASTS
RAW.NOAA_FORECASTS
  -> STAGING provider parsing
  -> INTERMEDIATE provider union and deduplication
  -> MARTS daily forecast and recommendation features
  -> FastAPI recommendation endpoint
```

Final forecast mart:

```text
MARTS.FCT_DAILY_FORECAST
```

Expected business columns:

```text
daily_forecast_id
city_id
city_name
forecast_date
selected_provider
temp_min_c
temp_max_c
temp_avg_c
precip_probability
wind_kmh
uv_index
condition
```

The recommendation engine can then apply rules such as:

```text
if temp_avg_c < 10 -> coat
if precip_probability >= 0.7 -> umbrella
if wind_kmh >= 30 -> windbreaker
if uv_index >= 6 -> sunglasses and sunscreen
```

## Additional Providers To Consider

### Open-Meteo Air Quality API

Why it helps:

- Adds air quality and environmental signals.
- Useful for sensitive users, outdoor comfort, and future health-oriented recommendations.
- Low integration complexity because it follows the Open-Meteo style.

Possible outfit/product use cases:

```text
poor air quality -> suggest mask
high pollen/dust -> warn allergy-sensitive users
high UV plus poor air quality -> suggest reduced outdoor exposure
```

Recommended priority:

```text
High, after core weather dbt models work
```

Reference:

```text
https://open-meteo.com/en/docs/air-quality-api
```

### MET Norway Locationforecast API

Why it helps:

- Adds another public forecast provider.
- Useful for provider comparison and resilience.
- Good candidate for Europe-focused weather validation.

Possible business use cases:

```text
compare Open-Meteo vs MET Norway forecasts
fallback if one provider is unavailable
increase confidence for European cities
```

Recommended priority:

```text
Medium, after Open-Meteo and NOAA are fully modeled
```

Reference:

```text
https://docs.api.met.no/doc/locationforecast/Locationforecast.html
```

### Open-Meteo Meteo-France API

Why it helps:

- Useful if the product targets France or Central Europe.
- Can improve Paris/French city forecasts using Meteo-France models exposed through Open-Meteo.

Possible business use cases:

```text
better local forecast quality for France
compare global provider versus national model
stronger French-market story for the project
```

Recommended priority:

```text
Medium, especially if the demo focuses on Paris or France
```

Reference:

```text
https://open-meteo.com/en/docs/meteofrance-api
```

### Tomorrow.io

Why it helps:

- Commercial-grade weather intelligence API.
- Rich weather layers and real-time weather use cases.
- Useful later for premium features or production comparisons.

Tradeoff:

- Requires API key and provider account management.
- Better for a later sprint after the open/free provider pipeline is stable.

Possible business use cases:

```text
hyperlocal alerts
premium weather insights
more detailed condition layers
commercial provider comparison
```

Recommended priority:

```text
Low for the MVP, useful later
```

Reference:

```text
https://docs.tomorrow.io/reference/welcome
```

## Recommended Provider Roadmap

```text
1. Finish Open-Meteo and NOAA transformations.
2. Add Open-Meteo Air Quality for comfort and health signals.
3. Add MET Norway for provider diversity.
4. Add Meteo-France model endpoint if France becomes a main market.
5. Add Tomorrow.io later if premium/commercial features are needed.
```

## Interview Explanation

The ingestion layer stores raw forecast payloads from Open-Meteo and NOAA in Snowflake. The raw layer preserves the original provider responses, making the pipeline replayable and auditable. dbt then parses and standardizes the weather signals into daily city forecasts. These forecasts feed the recommendation engine, which maps weather conditions to outfit decisions such as outer layer, umbrella, windbreaker, sunglasses, and sunscreen.
