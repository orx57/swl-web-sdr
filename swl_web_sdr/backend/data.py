import json
import random

import pandas as pd
import requests
import reverse_geocoder as rg
import streamlit as st
from vgrid.utils import maidenhead

import config


# Function to load CSV data
def load_csv(url, filters):
    return pd.read_csv(url)


# Function to load JSON data
def load_json(url, filters):
    response = requests.get(url)
    data = json.loads(response.text)

    # Reformat SNR values
    if "devices" in data:
        for device in data["devices"]:
            if "snr" in device:
                # Replace the comma by dot in SNR value
                device["snr"] = float(device["snr"].replace(",", "."))

    return data


# Function to load data with caching
def load_data(url, data_type, load=False, filters=None):
    if load:
        try:
            return loading_functions[data_type](url, filters)
        except KeyError:
            raise ValueError(f"Unsupported data type: {data_type}")
    else:
        return None


# Function to deduplicate devices
def deduplicate_devices(devices):
    """Remove duplicate devices based on URL"""
    unique_devices = {}
    for device in devices:
        url = device.get("url")
        if url:
            # Keep only the first occurrence or update if better status
            if url not in unique_devices or (
                device.get("status") == "active"
                and unique_devices[url].get("status") != "active"
            ):
                unique_devices[url] = device
    return list(unique_devices.values())


def get_grid_locator(gps_data):
    """Convert GPS coordinates to Maidenhead Grid Locator and get grid center"""
    if not gps_data:
        return None
    try:
        # If it's a string, try different formats
        if isinstance(gps_data, str):
            # Clean the string from parentheses and spaces
            clean_coords = gps_data.strip("() ").replace(" ", "")
            # Format "(lat, lon)" or "lat,lon"
            lat, lon = map(float, clean_coords.split(","))
        # If it's already a dict/list with lat/lon
        elif isinstance(gps_data, (dict, list)):
            if isinstance(gps_data, dict):
                lat = float(gps_data.get("lat", gps_data.get("latitude")))
                lon = float(gps_data.get("lon", gps_data.get("longitude")))
            else:
                lat, lon = map(float, gps_data[:2])

        # Get Maidenhead code
        grid_code = maidenhead.toMaiden(lat, lon, 3)
        return grid_code

    except Exception:
        return None


@st.cache_data(persist=True, show_spinner="Loading geocoding data...")
def get_country_from_gps(gps_data):
    """Get location details from GPS coordinates using reverse_geocoder with Streamlit persistent cache"""
    if not gps_data:
        return None
    try:
        # Parse coordinates comme avant
        if isinstance(gps_data, str):
            clean_coords = gps_data.strip("() ").replace(" ", "")
            lat, lon = map(float, clean_coords.split(","))
        elif isinstance(gps_data, (dict, list)):
            if isinstance(gps_data, dict):
                lat = float(gps_data.get("lat", gps_data.get("latitude")))
                lon = float(gps_data.get("lon", gps_data.get("longitude")))
            else:
                lat, lon = map(float, gps_data[:2])

        # Utilise reverse_geocoder avec les coordonnées exactes
        result = rg.search((lat, lon))
        if result and len(result) > 0:
            location = result[0]
            return {
                "country_code": location.get("cc", "").upper(),
                "city": location.get("name", ""),
                "region": location.get("admin1", ""),
            }

    except Exception as e:
        # st.error(_("Geocoding error: {error}").format(error=str(e)))  # WTF
        return None

    return None


def format_gps(gps_str):
    """Format GPS coordinates in a human readable format: 48.8567°N, 2.3508°E"""
    if not gps_str:
        return None
    try:
        # Clean the string from parentheses and spaces
        clean_coords = gps_str.strip("() ").replace(" ", "")
        lat, lon = map(float, clean_coords.split(","))

        # Ajout des traductions pour les points cardinaux
        lat_dir = _("N") if lat >= 0 else _("S")
        lon_dir = _("E") if lon >= 0 else _("W")

        # Format avec traduction
        return _("{lat:.4f}°{lat_dir}, {lon:.4f}°{lon_dir}").format(
            lat=abs(lat), lat_dir=lat_dir, lon=abs(lon), lon_dir=lon_dir
        )
    except Exception:
        return gps_str


# Generic aggregation of data from all sources
def aggregate_devices(data_sources):
    all_devices = []
    for source_name, source_data in data_sources.items():
        if source_data and "devices" in source_data:
            devices = deduplicate_devices(source_data["devices"])
            source_display_name = config.data_sources[source_name]["name"]
            for device in devices:
                device["source"] = source_display_name
                device["grid"] = get_grid_locator(device.get("gps"))

                # Convert bands to MHz format
                if (
                    "bands" in device
                    and isinstance(device["bands"], str)
                    and "-" in device["bands"]
                ):
                    try:
                        start, end = map(float, device["bands"].split("-"))
                        device["bands"] = f"{start / 1e6:.2f}-{end / 1e6:.2f} MHz"
                    except ValueError:
                        pass  # Keep the original value if conversion fails

                # Récupération des infos de géolocalisation enrichies
                location = get_country_from_gps(device.get("gps"))
                if location:
                    device.update(location)

                # Calcul du ratio d'utilisation
                users = float(device.get("users", 0))
                max_users = float(device.get("max_users", 1))  # évite division par 0
                device["users_ratio"] = (
                    min((users / max_users) * 100, 100) if max_users > 0 else 0
                )

                # Format GPS coordinates after
                if device.get("gps"):
                    device["gps"] = format_gps(device["gps"])
            all_devices.extend(devices)
    return all_devices


def get_random_available_sdr(devices):
    """Sélectionne au hasard un WebSDR actif avec de la place disponible"""
    available_devices = [
        device
        for device in devices
        if device.get("status") == "active"
        and device.get("users_ratio", 100) < 100
        and device.get("url")
    ]
    return random.choice(available_devices) if available_devices else None


# Dictionary of loading functions
loading_functions = {
    "csv": load_csv,
    "json": load_json,
}
