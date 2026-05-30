
create warehouse if not exists WOOTD_WH
  warehouse_size = XSMALL
  auto_suspend = 60
  auto_resume = true
  initially_suspended = true;

create database if not exists WOOTD_DB;

create schema if not exists WOOTD_DB.RAW;
create schema if not exists WOOTD_DB.STAGING;
create schema if not exists WOOTD_DB.INTERMEDIATE;
create schema if not exists WOOTD_DB.MARTS;

create table if not exists WOOTD_DB.RAW.WEATHER_FORECAST_PAYLOADS (
  INGESTION_ID string default uuid_string(),
  PROVIDER string not null,
  CITY_NAME string not null,
  COUNTRY string not null,
  LATITUDE float,
  LONGITUDE float,
  INGESTED_AT timestamp_tz not null,
  PAYLOAD variant not null
);

create table if not exists WOOTD_DB.RAW.OPEN_METEO_FORECASTS (
  INGESTION_ID string default uuid_string(),
  PROVIDER string not null,
  CITY_NAME string not null,
  LATITUDE float,
  LONGITUDE float,
  INGESTED_AT timestamp_tz not null,
  PAYLOAD variant not null
);

create table if not exists WOOTD_DB.RAW.NOAA_FORECASTS (
  INGESTION_ID string default uuid_string(),
  PROVIDER string not null,
  CITY_NAME string not null,
  INGESTED_AT timestamp_tz not null,
  PAYLOAD variant not null
);

create table if not exists WOOTD_DB.RAW.USER_FEEDBACK (
  FEEDBACK_ID string default uuid_string(),
  RECOMMENDATION_ID string not null,
  RATING integer not null,
  NOTES string,
  CREATED_AT timestamp_tz default current_timestamp()
);

create table if not exists WOOTD_DB.RAW.INGESTION_RUNS (
  RUN_ID string default uuid_string(),
  PROVIDER string not null,
  RUN_STARTED_AT timestamp_tz not null,
  RUN_FINISHED_AT timestamp_tz not null,
  STATUS string not null,
  ROWS_LOADED integer not null,
  MESSAGE string
);
