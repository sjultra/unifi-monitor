#!/usr/bin/env python3
"""
UDM Pro DHCP Reservations Query Script
Connects directly to UDM Pro local API using API key authentication
"""

import requests
import json
import urllib3
from typing import List, Dict, Optional, Set
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

BASE_URL = os.getenv("UNIFI_BASE_URL", "")
API_KEY = os.getenv("UNIFI_API_KEY", "")

def log(msg):
    print(f"[LOG] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def log_warning(msg):
    print(f"[WARNING] {msg}")

class UDMProClient:
    def __init__(self, host: str, api_key: str, port: int = 443):
        """
        Initialize UDM Pro client with API key authentication
        
        Args:
            host: IP address or hostname of UDM Pro
            api_key: API key for authentication
            port: HTTPS port (default 443)
        """
        self.host = host
        self.api_key = api_key
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate errors
        
        # Set up authentication headers
        self.session.headers.update({
            'X-API-KEY': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def test_connection(self) -> bool:
        """
        Test API key authentication
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        test_url = f"{self.base_url}/proxy/network/integration/v1/sites"
        
        try:
            response = self.session.get(test_url, timeout=10)
            if response.status_code == 200:
                log(f"✓ Successfully authenticated to UDM Pro at {self.host}")
                return True
            elif response.status_code == 401:
                log_error(f"✗ Authentication failed: Invalid API key")
                return False
            else:
                log_error(f"✗ Connection failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            log_error(f"✗ Connection error: {e}")
            return False
    
    def get_sites(self) -> List[Dict]:
        """
        Get all sites from the controller
        
        Returns:
            List of site dictionaries
        """
        sites_url = f"{self.base_url}/proxy/network/api/self/sites"
        try:
            response = self.session.get(sites_url, timeout=10)
            log(f"Sites API response: {response.status_code}")
            if response.status_code == 200:
                data = response.json().get('data', [])
                log(f"Found {len(data)} sites")
                return data
            else:
                log_error(f"Failed to get sites: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            log_error(f"Error getting sites: {e}")
            return []
    
    def get_dhcp_reservations(self, site_name: str = "default") -> List[Dict]:
        """
        Get DHCP reservations from a specific site
        
        Args:
            site_name: Site name (default is "default")
            
        Returns:
            List of DHCP reservation dictionaries
        """
        # Try the UDM Pro API endpoint for users with fixed IPs
        reservations_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/user"
        
        try:
            log(f"Trying users endpoint: {reservations_url}")
            response = self.session.get(reservations_url, timeout=10)
            log(f"Users API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                log(f"Found {len(data)} total users")
                
                # Filter for users with use_fixedip True (active DHCP reservations only)
                reservations = [
                    user for user in data 
                    if user.get('use_fixedip', False)
                ]
                log(f"Found {len(reservations)} users with DHCP reservations")
                return reservations
            else:
                log_error(f"Failed to get users: {response.status_code} - {response.text}")
                # Try alternative endpoint
                return self._get_dhcp_reservations_alt(site_name)
        except requests.exceptions.RequestException as e:
            log_error(f"Error getting users: {e}")
            return self._get_dhcp_reservations_alt(site_name)
    
    def _get_dhcp_reservations_alt(self, site_name: str = "default") -> List[Dict]:
        """
        Alternative method to get DHCP reservations from network configuration
        
        Args:
            site_name: Site name (default is "default")
            
        Returns:
            List of DHCP reservation dictionaries
        """
        networks_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/networkconf"
        
        try:
            log(f"Trying network config endpoint: {networks_url}")
            response = self.session.get(networks_url, timeout=10)
            log(f"Network config API response: {response.status_code}")
            
            if response.status_code == 200:
                networks = response.json().get('data', [])
                log(f"Found {len(networks)} networks")
                reservations = []
                
                for network in networks:
                    if 'dhcp_reservations' in network:
                        network_reservations = network['dhcp_reservations']
                        log(f"Network '{network.get('name', 'Unknown')}' has {len(network_reservations)} reservations")
                        for reservation in network_reservations:
                            reservation['network_name'] = network.get('name', 'Unknown')
                            reservations.append(reservation)
                
                log(f"Total DHCP reservations found: {len(reservations)}")
                return reservations
            else:
                log_error(f"Failed to get network configuration: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            log_error(f"Error getting network configuration: {e}")
            return []
    
    def get_all_clients(self, site_name: str = "default") -> List[Dict]:
        """
        Get all clients (active and known) from the site
        
        Args:
            site_name: Site name (default is "default")
            
        Returns:
            List of client dictionaries
        """
        clients_url = f"{self.base_url}/proxy/network/api/s/{site_name}/stat/sta"
        
        try:
            log(f"Getting all clients from: {clients_url}")
            response = self.session.get(clients_url, timeout=10)
            log(f"Clients API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                log(f"Found {len(data)} total clients")
                return data
            else:
                log_error(f"Failed to get clients: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            log_error(f"Error getting clients: {e}")
            return []
    
    def get_networks(self, site_name: str = "default") -> List[Dict]:
        """
        Get network configurations
        
        Args:
            site_name: Site name (default is "default")
            
        Returns:
            List of network dictionaries
        """
        networks_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/networkconf"
        
        try:
            response = self.session.get(networks_url, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                log_error(f"Failed to get networks: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            log_error(f"Error getting networks: {e}")
            return []
    
    def create_dhcp_reservation(self, mac_address: str, ip_address: str, 
                              name: str = None, hostname: str = None, 
                              site_name: str = "default") -> bool:
        """
        Create a DHCP reservation by creating a user with fixed IP
        
        Args:
            mac_address: MAC address of the device
            ip_address: IP address to reserve
            name: Friendly name for the device
            hostname: Hostname for the device
            site_name: Site name (default is "default")
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate inputs
        if not self._validate_mac_address(mac_address):
            log_error(f"Invalid MAC address format: {mac_address}")
            return False
        
        if not self._validate_ip_address(ip_address):
            log_error(f"Invalid IP address format: {ip_address}")
            return False
        
        # Check if MAC already exists
        existing_user = self._find_user_by_mac(mac_address, site_name)
        if existing_user:
            log(f"User with MAC {mac_address} already exists. Updating...")
            return self._update_user_fixed_ip(existing_user['_id'], ip_address, name, hostname, site_name)
        
        # Create new user with fixed IP
        user_data = {
            "mac": mac_address.lower(),
            "fixed_ip": ip_address,
            "use_fixedip": True,
            "name": name or f"Device-{mac_address}",
            "hostname": hostname or name or f"device-{mac_address.replace(':', '')}"
        }
        
        users_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/user"
        
        try:
            log(f"Creating DHCP reservation for {mac_address} -> {ip_address}")
            response = self.session.post(users_url, json=user_data, timeout=10)
            
            if response.status_code in [200, 201]:
                log(f"✓ Successfully created DHCP reservation for {mac_address}")
                return True
            else:
                log_error(f"Failed to create DHCP reservation: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            log_error(f"Error creating DHCP reservation: {e}")
            return False
    
    def delete_dhcp_reservation(self, mac_address: str, site_name: str = "default") -> bool:
        """
        Delete a DHCP reservation by removing fixed IP from user
        
        Args:
            mac_address: MAC address of the device
            site_name: Site name (default is "default")
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the user by MAC address
        user = self._find_user_by_mac(mac_address, site_name)
        if not user:
            log_error(f"No user found with MAC address: {mac_address}")
            return False
        
        # Remove fixed IP assignment
        return self._remove_user_fixed_ip(user['_id'], site_name)
    
    def _find_user_by_mac(self, mac_address: str, site_name: str = "default") -> Optional[Dict]:
        """Find a user by MAC address"""
        users_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/user"
        
        try:
            response = self.session.get(users_url, timeout=10)
            if response.status_code == 200:
                users = response.json().get('data', [])
                mac_normalized = normalize_mac_address(mac_address)
                
                for user in users:
                    user_mac_normalized = normalize_mac_address(user.get('mac', ''))
                    if user_mac_normalized == mac_normalized:
                        return user
            return None
        except requests.exceptions.RequestException:
            return None
    
    def _update_user_fixed_ip(self, user_id: str, ip_address: str, 
                             name: str = None, hostname: str = None,
                             site_name: str = "default") -> bool:
        """Update an existing user with fixed IP"""
        update_data = {
            "fixed_ip": ip_address,
            "use_fixedip": True
        }
        
        if name:
            update_data["name"] = name
        if hostname:
            update_data["hostname"] = hostname
        
        users_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/user/{user_id}"
        
        try:
            response = self.session.put(users_url, json=update_data, timeout=10)
            
            if response.status_code == 200:
                log(f"✓ Successfully updated user with fixed IP: {ip_address}")
                return True
            else:
                log_error(f"Failed to update user: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            log_error(f"Error updating user: {e}")
            return False
    
    def _remove_user_fixed_ip(self, user_id: str, site_name: str = "default") -> bool:
        """Remove fixed IP from user"""
        update_data = {
            "use_fixedip": False
        }
        
        users_url = f"{self.base_url}/proxy/network/api/s/{site_name}/rest/user/{user_id}"
        
        try:
            response = self.session.put(users_url, json=update_data, timeout=10)
            
            if response.status_code == 200:
                log(f"✓ Successfully removed fixed IP from user")
                return True
            else:
                log_error(f"Failed to remove fixed IP: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            log_error(f"Error removing fixed IP: {e}")
            return False
    
    def _validate_mac_address(self, mac_address: str) -> bool:
        """Validate MAC address format"""
        import re
        # Accept formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX
        pattern = r'^([0-9A-Fa-f]{2}[:-]?){5}[0-9A-Fa-f]{2}$'
        return bool(re.match(pattern, mac_address))
    
    def _validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.IPv4Address(ip_address)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def get_available_ip_ranges(self, site_name: str = "default") -> List[Dict]:
        """
        Get available IP ranges from network configurations
        
        Args:
            site_name: Site name (default is "default")
            
        Returns:
            List of network ranges with DHCP info
        """
        networks = self.get_networks(site_name)
        ranges = []
        
        for network in networks:
            if network.get('purpose') == 'corporate' and 'ip_subnet' in network:
                subnet = network['ip_subnet']
                dhcp_start = network.get('dhcpd_start')
                dhcp_stop = network.get('dhcpd_stop')
                
                range_info = {
                    'network_name': network.get('name', 'Unknown'),
                    'subnet': subnet,
                    'dhcp_enabled': network.get('dhcpd_enabled', False),
                    'dhcp_range_start': dhcp_start,
                    'dhcp_range_end': dhcp_stop,
                    'gateway': network.get('dhcpd_gateway', network.get('ip_subnet', '').split('/')[0])
                }
                ranges.append(range_info)
        
        return ranges

def normalize_mac_address(mac: str) -> str:
    """Normalize MAC address to lowercase without separators"""
    return mac.lower().replace(':', '').replace('-', '')

def format_reservation_info(reservation: Dict) -> str:
    """Format DHCP reservation information for display"""
    name = reservation.get('name', reservation.get('hostname', 'Unknown'))
    hostname = reservation.get('hostname', 'N/A')
    mac = reservation.get('mac', 'N/A')
    fixed_ip = reservation.get('fixed_ip', reservation.get('ip', 'N/A'))
    last_seen = reservation.get('last_seen', 0)
    network_name = reservation.get('network_name', 'N/A')
    
    # Convert last_seen timestamp to readable format
    if last_seen > 0:
        last_seen_date = datetime.fromtimestamp(last_seen).strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_seen_date = 'Never'
    
    return f"""
  Name: {name}
  Hostname: {hostname}
  MAC Address: {mac.upper() if mac != 'N/A' else mac}
  Reserved IP: {fixed_ip}
  Network: {network_name}
  Last Seen: {last_seen_date}
  {'─' * 50}"""

def format_json_output(reservations: List[Dict]) -> str:
    """Format reservations as JSON for programmatic use"""
    formatted_reservations = []
    for reservation in reservations:
        formatted_reservation = {
            'name': reservation.get('name', reservation.get('hostname', 'Unknown')),
            'hostname': reservation.get('hostname', 'N/A'),
            'mac_address': reservation.get('mac', 'N/A'),
            'reserved_ip': reservation.get('fixed_ip', reservation.get('ip', 'N/A')),
            'network_name': reservation.get('network_name', 'N/A'),
            'last_seen': reservation.get('last_seen', 0)
        }
        formatted_reservations.append(formatted_reservation)
    
    return json.dumps(formatted_reservations, indent=2)

def sync_reservations_from_json(client: UDMProClient, json_file: str, site_name: str = "default", 
                               dry_run: bool = False, confirm_destructive: bool = True):
    """
    Sync DHCP reservations from a JSON file - removes existing reservations not in file
    and creates/updates reservations from file
    
    Expected JSON format:
    [
        {
            "name": "Living Room TV",
            "hostname": "living-room-tv",
            "mac_address": "aa:bb:cc:dd:ee:ff",
            "reserved_ip": "192.168.37.38",
            "network_name": "N/A",
            "last_seen": 0
        },
        ...
    ]
    
    Args:
        client: UDMProClient instance
        json_file: Path to JSON file containing desired reservations
        site_name: Site name (default is "default")
        dry_run: If True, only show what would be done without making changes
        confirm_destructive: If True, ask for confirmation before removing reservations
    """
    try:
        with open(json_file, 'r') as f:
            desired_reservations = json.load(f)
    except FileNotFoundError:
        log_error(f"JSON file not found: {json_file}")
        return False
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON format: {e}")
        return False
    
    if not isinstance(desired_reservations, list):
        log_error("JSON file must contain an array of reservation objects")
        return False
    
    # Validate JSON data
    valid_reservations = []
    for i, reservation in enumerate(desired_reservations):
        mac = reservation.get('mac_address')
        ip = reservation.get('reserved_ip')
        
        if not mac or not ip:
            log_error(f"Skipping reservation {i+1}: Missing required fields (mac_address, reserved_ip)")
            continue
        
        if not client._validate_mac_address(mac):
            log_error(f"Skipping reservation {i+1}: Invalid MAC address format: {mac}")
            continue
        
        if not client._validate_ip_address(ip):
            log_error(f"Skipping reservation {i+1}: Invalid IP address format: {ip}")
            continue
        
        valid_reservations.append(reservation)
    
    if not valid_reservations:
        log_error("No valid reservations found in JSON file")
        return False
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Syncing DHCP reservations from {json_file}")
    print(f"Target: {len(valid_reservations)} reservations")
    print("=" * 60)
    
    # Get existing reservations
    log("Getting existing DHCP reservations...")
    existing_reservations = client.get_dhcp_reservations(site_name)
    
    # Create dictionaries for easier comparison
    existing_by_mac = {
        normalize_mac_address(res.get('mac', '')): res 
        for res in existing_reservations if res.get('mac')
    }
    desired_by_mac = {
        normalize_mac_address(res['mac_address']): res 
        for res in valid_reservations
    }
    
    # Find reservations to remove (exist on UDM but not in JSON)
    macs_to_remove = set(existing_by_mac.keys()) - set(desired_by_mac.keys())
    reservations_to_remove = [existing_by_mac[mac] for mac in macs_to_remove]
    
    # Find reservations to create/update
    reservations_to_create = []
    reservations_to_update = []
    
    for mac_norm, desired in desired_by_mac.items():
        if mac_norm in existing_by_mac:
            existing = existing_by_mac[mac_norm]
            # Check if update is needed
            if (existing.get('fixed_ip') != desired['reserved_ip'] or
                existing.get('name') != desired.get('name') or
                existing.get('hostname') != desired.get('hostname')):
                reservations_to_update.append(desired)
            # else: reservation is already correct, no action needed
        else:
            reservations_to_create.append(desired)
    
    # Show what will be done
    print(f"\nCurrent state: {len(existing_reservations)} existing reservations")
    print(f"Desired state: {len(valid_reservations)} reservations from JSON")
    print(f"Actions needed:")
    print(f"  - Remove: {len(reservations_to_remove)} reservations")
    print(f"  - Create: {len(reservations_to_create)} reservations") 
    print(f"  - Update: {len(reservations_to_update)} reservations")
    print(f"  - No change: {len(valid_reservations) - len(reservations_to_create) - len(reservations_to_update)} reservations")
    
    if reservations_to_remove:
        print(f"\nReservations to be REMOVED:")
        for res in reservations_to_remove:
            name = res.get('name', res.get('hostname', 'Unknown'))
            mac = res.get('mac', 'N/A')
            ip = res.get('fixed_ip', 'N/A')
            print(f"  - {name} ({mac.upper()}) -> {ip}")
    
    if reservations_to_create:
        print(f"\nReservations to be CREATED:")
        for res in reservations_to_create:
            name = res.get('name', 'Unknown')
            mac = res.get('mac_address', 'N/A')
            ip = res.get('reserved_ip', 'N/A')
            print(f"  - {name} ({mac.upper()}) -> {ip}")
    
    if reservations_to_update:
        print(f"\nReservations to be UPDATED:")
        for res in reservations_to_update:
            name = res.get('name', 'Unknown')
            mac = res.get('mac_address', 'N/A')
            ip = res.get('reserved_ip', 'N/A')
            print(f"  - {name} ({mac.upper()}) -> {ip}")
    
    if dry_run:
        print(f"\n[DRY RUN] No changes will be made. Remove --dry-run to execute.")
        return True
    
    # Confirm destructive operation
    if reservations_to_remove and confirm_destructive:
        print(f"\n⚠️  WARNING: This will REMOVE {len(reservations_to_remove)} existing DHCP reservations!")
        print("This action cannot be undone.")
        response = input("Do you want to continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("Operation cancelled.")
            return False
    
    # Remove existing reservations not in JSON
    removed_count = 0
    if reservations_to_remove:
        print(f"\nRemoving {len(reservations_to_remove)} existing reservations...")
        for res in reservations_to_remove:
            mac = res.get('mac', '')
            name = res.get('name', res.get('hostname', 'Unknown'))
            
            print(f"  Removing: {name} ({mac.upper()})")
            success = client.delete_dhcp_reservation(mac, site_name)
            if success:
                removed_count += 1
            else:
                log_error(f"Failed to remove reservation for {mac}")
    
    # Create/update reservations from JSON
    total_changes = len(reservations_to_create) + len(reservations_to_update)
    if total_changes > 0:
        print(f"\nProcessing {total_changes} reservation changes...")
        create_success_count = 0
        update_success_count = 0
        
        # Create new reservations
        for i, reservation in enumerate(reservations_to_create, 1):
            mac = reservation['mac_address']
            ip = reservation['reserved_ip']
            name = reservation.get('name')
            hostname = reservation.get('hostname')
            
            print(f"  [CREATE {i}/{len(reservations_to_create)}] {mac.upper()} -> {ip}")
            
            success = client.create_dhcp_reservation(mac, ip, name, hostname, site_name)
            if success:
                create_success_count += 1
            else:
                log_error(f"Failed to create reservation for {mac}")
        
        # Update existing reservations
        for i, reservation in enumerate(reservations_to_update, 1):
            mac = reservation['mac_address']
            ip = reservation['reserved_ip']
            name = reservation.get('name')
            hostname = reservation.get('hostname')
            
            print(f"  [UPDATE {i}/{len(reservations_to_update)}] {mac.upper()} -> {ip}")
            
            success = client.create_dhcp_reservation(mac, ip, name, hostname, site_name)
            if success:
                update_success_count += 1
            else:
                log_error(f"Failed to update reservation for {mac}")
    else:
        print(f"\nNo reservations need to be created or updated.")
        create_success_count = 0
        update_success_count = 0
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Sync completed:")
    print(f"  ✓ Removed: {removed_count}/{len(reservations_to_remove)} reservations")
    print(f"  ✓ Created: {create_success_count}/{len(reservations_to_create)} reservations")
    print(f"  ✓ Updated: {update_success_count}/{len(reservations_to_update)} reservations") 
    print(f"  ✓ Unchanged: {len(valid_reservations) - len(reservations_to_create) - len(reservations_to_update)} reservations")
    
    total_expected = len(reservations_to_remove) + len(reservations_to_create) + len(reservations_to_update)
    total_successful = removed_count + create_success_count + update_success_count
    
    if (removed_count == len(reservations_to_remove) and 
        create_success_count == len(reservations_to_create) and 
        update_success_count == len(reservations_to_update)):
        print(f"  🎉 All operations successful!")
        return True
    else:
        print(f"  ⚠️  Some operations failed. Check the logs above.")
        return False

def create_reservations_from_json(client: UDMProClient, json_file: str, site_name: str = "default"):
    """
    Create DHCP reservations from a JSON file (legacy function - doesn't remove existing)
    
    Expected JSON format:
    [
        {
            "name": "Living Room TV",
            "hostname": "living-room-tv",
            "mac_address": "aa:bb:cc:dd:ee:ff",
            "reserved_ip": "192.168.37.38",
            "network_name": "N/A",
            "last_seen": 0
        },
        ...
    ]
    """
    log_warning("Using legacy create mode. Consider using --sync for full synchronization.")
    
    try:
        with open(json_file, 'r') as f:
            reservations_data = json.load(f)
    except FileNotFoundError:
        log_error(f"JSON file not found: {json_file}")
        return False
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON format: {e}")
        return False
    
    if not isinstance(reservations_data, list):
        log_error("JSON file must contain an array of reservation objects")
        return False
    
    print(f"Creating {len(reservations_data)} DHCP reservations from {json_file}")
    print("=" * 60)
    
    success_count = 0
    total_count = len(reservations_data)
    
    for i, reservation in enumerate(reservations_data, 1):
        mac = reservation.get('mac_address')
        ip = reservation.get('reserved_ip') 
        name = reservation.get('name')
        hostname = reservation.get('hostname')
        
        if not mac or not ip:
            log_error(f"[{i}/{total_count}] Missing required fields (mac_address, reserved_ip) in reservation: {reservation}")
            continue
            
        print(f"[{i}/{total_count}] Creating reservation: {mac} -> {ip}")
        
        success = client.create_dhcp_reservation(mac, ip, name, hostname, site_name)
        if success:
            success_count += 1
        else:
            log_error(f"Failed to create reservation for {mac}")
    
    print(f"\nCompleted: {success_count}/{total_count} reservations created successfully")
    return success_count == total_count

def main():
    """Main function to query and manage DHCP reservations"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='UDM Pro DHCP Reservations Management')
    parser.add_argument('--create-from-json', metavar='FILE', 
                       help='Create reservations from JSON file (legacy mode)')
    parser.add_argument('--sync-from-json', metavar='FILE',
                       help='Sync reservations from JSON file (removes existing not in file)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes (use with --sync-from-json)')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation prompts for destructive operations')
    parser.add_argument('--site', default='default',
                       help='Site name (default: default)')
    
    args = parser.parse_args()
    
    # Legacy command line support
    if len(sys.argv) == 3 and sys.argv[1] == "--create-from-json":
        args.create_from_json = sys.argv[2]
    
    # Use the environment variables or defaults
    host = BASE_URL.replace('https://', '').replace('http://', '')
    api_key = API_KEY
    
    if not api_key:
        log_error("No API key provided. Set UNIFI_API_KEY environment variable")
        sys.exit(1)
    
    print(f"Connecting to UDM Pro at: {host}")
    print(f"Using API key: {api_key[:10]}...")
    
    # Initialize client
    client = UDMProClient(host, api_key)
    
    # Test connection
    if not client.test_connection():
        log_error("Failed to connect to UDM Pro. Please check your API key and network connection.")
        sys.exit(1)
    
    # Handle JSON file operations
    if args.sync_from_json:
        success = sync_reservations_from_json(
            client, 
            args.sync_from_json, 
            args.site,
            dry_run=args.dry_run,
            confirm_destructive=not args.no_confirm
        )
        sys.exit(0 if success else 1)
    
    elif args.create_from_json:
        success = create_reservations_from_json(client, args.create_from_json, args.site)
        sys.exit(0 if success else 1)
    
    # Default behavior: list existing reservations
    # Get sites
    sites = client.get_sites()
    if sites:
        log(f"Available sites: {', '.join([site.get('name', 'Unknown') for site in sites])}")
        site_name = sites[0].get('name', 'default')
    else:
        log("No sites found, using 'default'")
        site_name = 'default'
    
    print(f"\nQuerying DHCP reservations from site: {site_name}")
    print("=" * 60)
    
    # Try to get DHCP reservations
    reservations = client.get_dhcp_reservations(site_name)
    
    if not reservations:
        log("No DHCP reservations found. Trying to get all clients with fixed IPs...")
        # Get all clients and filter for those with reserved IPs
        clients = client.get_all_clients(site_name)
        reservations = [client for client in clients if client.get('fixed_ip') or client.get('use_fixedip')]
        source = "clients database"
    else:
        source = "DHCP configuration"
    
    if not reservations:
        print("No DHCP reservations found in any method.")
        print("\nUsage examples:")
        print("  List reservations:     python script.py")
        print("  Create from JSON:      python script.py --create-from-json reservations.json")
        print("  Sync from JSON:        python script.py --sync-from-json reservations.json")
        print("  Dry run sync:          python script.py --sync-from-json reservations.json --dry-run")
        return
    
    print(f"Found {len(reservations)} DHCP reservation(s) from {source}:")
    
    for i, reservation in enumerate(reservations, 1):
        print(f"\n[{i}] DHCP Reservation:")
        print(format_reservation_info(reservation))
    
    # Also output JSON for easy parsing
    print(f"\n\nJSON Output:")
    print("=" * 60)
    print(format_json_output(reservations))
    
    print(f"\nUsage examples:")
    print("  Create from JSON:      python script.py --create-from-json reservations.json")
    print("  Sync from JSON:        python script.py --sync-from-json reservations.json")
    print("  Dry run sync:          python script.py --sync-from-json reservations.json --dry-run")

if __name__ == "__main__":
    main()