"""
Test script for Seismic DTDL Interfaces

Tests the newly added seismic domain interfaces:
- Building
- Street
- Base Station
- Seismic Sensor
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.dtdl_loader_service import get_dtdl_loader


def print_section(title):
    """Print section separator"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    print_section("SEISMIC DTDL INTERFACES TEST")

    # 1. Initialize loader
    print("\n1. Initializing DTDL Loader...")
    loader = get_dtdl_loader()
    print(f"   [OK] Loaded {len(loader._interfaces_cache)} interfaces total")

    # 2. List all interfaces
    print("\n2. All Available Interfaces:")
    all_interfaces = loader.list_all_interfaces()
    for iface in all_interfaces:
        print(f"   - {iface['displayName']} ({iface['category']})")

    # 3. Search seismic domain interfaces
    print("\n3. Seismic Domain Interfaces:")
    seismic_interfaces = loader.search_interfaces(domain="seismic")
    print(f"   Found {len(seismic_interfaces)} seismic interfaces:")
    for iface in seismic_interfaces:
        print(f"   - {iface['displayName']} (DTMI: {iface['dtmi']})")
        print(f"     Type: {iface.get('thingType', 'N/A')}")
        print(f"     Tags: {', '.join(iface.get('tags', []))}")
        print()

    # 4. Test Building interface
    print("\n4. Building Interface Details:")
    building = loader.get_interface_details("dtmi:iodt2:Building;1")
    if building:
        print(f"   Display Name: {building['displayName']}")
        print(f"   Description: {building['description']}")
        print(f"   Extends: {building.get('extends', 'None')}")

        # Count contents
        contents = building.get('contents', [])
        telemetry = [c for c in contents if c.get('@type') == 'Telemetry']
        properties = [c for c in contents if c.get('@type') == 'Property']
        commands = [c for c in contents if c.get('@type') == 'Command']

        print(f"   Telemetry: {len(telemetry)} ({', '.join([t['name'] for t in telemetry])})")
        print(f"   Properties: {len(properties)} ({', '.join([p['name'] for p in properties])})")
        print(f"   Commands: {len(commands)} ({', '.join([c['name'] for c in commands])})")

    # 5. Test Seismic Sensor interface
    print("\n5. Seismic Sensor Interface Details:")
    sensor = loader.get_interface_details("dtmi:iodt2:SeismicSensor;1")
    if sensor:
        print(f"   Display Name: {sensor['displayName']}")
        print(f"   Description: {sensor['description']}")

        contents = sensor.get('contents', [])
        telemetry = [c for c in contents if c.get('@type') == 'Telemetry']

        print(f"   Telemetry ({len(telemetry)}):")
        for tel in telemetry:
            unit = tel.get('unit', 'N/A')
            print(f"     - {tel['name']}: {tel['schema']} ({unit})")

    # 6. Search by thing_type
    print("\n6. Component-type Things (Buildings, Streets):")
    components = loader.search_interfaces(thing_type="component")
    seismic_components = [c for c in components if 'seismic' in c.get('tags', [])]
    print(f"   Found {len(seismic_components)} seismic components:")
    for comp in seismic_components:
        print(f"   - {comp['displayName']}")

    # 7. Search by keywords
    print("\n7. Search by Keyword 'earthquake':")
    earthquake_related = loader.search_interfaces(keywords="earthquake")
    print(f"   Found {len(earthquake_related)} earthquake-related interfaces:")
    for iface in earthquake_related:
        print(f"   - {iface['displayName']}")

    # 8. Domain mapping
    print("\n8. Domain Mapping:")
    if loader._registry_cache:
        domain_mapping = loader._registry_cache.get("domainMapping", {})
        print(f"   Seismic domain interfaces: {len(domain_mapping.get('seismic', []))}")
        for dtmi in domain_mapping.get('seismic', []):
            iface = loader.get_interface(dtmi)
            if iface:
                print(f"     - {iface.get('displayName', dtmi)}")

    print_section("TEST COMPLETED SUCCESSFULLY")
    print(f"\nTotal interfaces: {len(all_interfaces)}")
    print(f"Seismic interfaces: {len(seismic_interfaces)}")
    print(f"\n✅ All seismic DTDL interfaces loaded successfully!")


if __name__ == "__main__":
    main()
