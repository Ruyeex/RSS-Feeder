#!/usr/bin/env python3
"""
VS Mod DB RSS Feed Generator
Fetches the latest mod updates and generates an RSS feed
"""

import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import os


def generate_rss_feed():
    """Generate RSS feed for VS Mod DB updates"""
    
    # Create root RSS element
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    # Add channel metadata
    ET.SubElement(channel, 'title').text = 'VS Mod DB Updates'
    ET.SubElement(channel, 'link').text = 'https://mods.vintagestory.at/'
    ET.SubElement(channel, 'description').text = 'Latest updates from VS Mod Database'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Try to fetch mods data (add your actual API endpoint)
    try:
        # Example: fetch from VS Mod DB API
        response = requests.get('https://mods.vintagestory.at/api/mods', timeout=10)
        response.raise_for_status()
        mods = response.json()
        
        # Add items for each mod
        if isinstance(mods, list):
            for mod in mods[:20]:  # Limit to latest 20
                item = ET.SubElement(channel, 'item')
                ET.SubElement(item, 'title').text = mod.get('name', 'Unknown Mod')
                ET.SubElement(item, 'link').text = f"https://mods.vintagestory.at/show/mod/{mod.get('id', '')}"
                ET.SubElement(item, 'description').text = mod.get('description', '')
                ET.SubElement(item, 'pubDate').text = mod.get('updated', datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000'))
    
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch mod data: {e}")
        # Continue with empty feed rather than failing completely
    
    # Pretty print and save
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')
    # Remove extra blank lines
    xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
    
    output_file = 'vsmoddb_updates.xml'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"RSS feed generated: {output_file}")


if __name__ == '__main__':
    generate_rss_feed()
