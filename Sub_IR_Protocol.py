#!/usr/bin/env python3
"""
Interactive Flipper Zero Protocol File Generator
Creates custom Sub-GHz and Infrared protocol files with interactive wizards
Compatible with Termux and other Python environments
"""

import os
import json
import argparse
import sys
import re
from datetime import datetime
from typing import List, Dict, Union, Optional, Tuple
import time
import random

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def disable():
        Colors.HEADER = Colors.BLUE = Colors.CYAN = ''
        Colors.GREEN = Colors.YELLOW = Colors.RED = Colors.ENDC = Colors.BOLD = ''

class InteractiveFlipperGenerator:
    def __init__(self):
        self.version = "2.0.0"
        
        # CORRECTED protocol specifications based on actual Flipper Zero GitHub examples
        self.subghz_protocols = {
            "Princeton": {"bits": 24, "key_bytes": 8, "needs_te": True, "default_te": 400, "description": "Common garage door openers (24-bit data, 8-byte key)"},
            "Nice_Flo": {"bits": 12, "key_bytes": 3, "needs_te": False, "description": "Nice rolling code remotes (12-bit)"},
            "Came": {"bits": 12, "key_bytes": 3, "needs_te": False, "description": "CAME gate remotes (12-bit)"},
            "Linear": {"bits": 10, "key_bytes": 3, "needs_te": False, "description": "Linear garage door openers (10-bit)"},
            "Gate_TX": {"bits": 24, "key_bytes": 6, "needs_te": False, "description": "Generic gate transmitters (24-bit)"},
            "Chamberlain": {"bits": 32, "key_bytes": 8, "needs_te": False, "description": "Chamberlain garage doors (32-bit)"},
            "DoorHan": {"bits": 24, "key_bytes": 6, "needs_te": False, "description": "DoorHan gate systems (24-bit)"},
            "Somfy_Telis": {"bits": 56, "key_bytes": 14, "needs_te": False, "description": "Somfy window blinds (56-bit)"},
            "Star_Line": {"bits": 64, "key_bytes": 16, "needs_te": False, "description": "StarLine car alarms (64-bit)"},
            "Holtek": {"bits": 40, "key_bytes": 10, "needs_te": False, "description": "Holtek microcontroller remotes (40-bit)"},
            "RAW": {"bits": 0, "key_bytes": 0, "needs_te": False, "description": "Custom raw timing data"}
        }
        
        # CORRECTED IR protocol specifications
        self.ir_protocols = {
            "NEC": {"address_bits": 8, "command_bits": 8, "description": "Most common IR protocol (8+8 bits)"},
            "NECext": {"address_bits": 16, "command_bits": 8, "description": "Extended NEC protocol (16+8 bits)"},
            "Samsung32": {"address_bits": 8, "command_bits": 8, "description": "Samsung TVs and devices (8+8 bits)"},
            "RC5": {"address_bits": 5, "command_bits": 6, "description": "Philips RC5 protocol (5+6 bits)"},
            "RC6": {"address_bits": 8, "command_bits": 8, "description": "Philips RC6 protocol (8+8 bits)"},
            "SIRC": {"address_bits": 5, "command_bits": 7, "description": "Sony SIRC 12-bit (5+7 bits)"},
            "SIRC15": {"address_bits": 8, "command_bits": 7, "description": "Sony SIRC 15-bit (8+7 bits)"},
            "SIRC20": {"address_bits": 13, "command_bits": 7, "description": "Sony SIRC 20-bit (13+7 bits)"},
            "RAW": {"address_bits": 0, "command_bits": 0, "description": "Custom raw IR timing"}
        }
        
        self.common_frequencies = {
            "315 MHz": 315000000,
            "433.92 MHz": 433920000,
            "868 MHz": 868000000,
            "915 MHz": 915000000
        }

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Colors.CYAN}{'='*60}")
        print(f"{Colors.BOLD}🐬 Interactive Flipper Zero Protocol Generator v{self.version}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

    def main_menu(self):
        """Display main menu and handle selection"""
        while True:
            print(f"\n{Colors.HEADER}Main Menu:{Colors.ENDC}")
            print(f"{Colors.BLUE}1.{Colors.ENDC} Create Sub-GHz Protocol File")
            print(f"{Colors.BLUE}2.{Colors.ENDC} Create Infrared Protocol File")
            print(f"{Colors.BLUE}3.{Colors.ENDC} Signal Analysis Tools")
            print(f"{Colors.BLUE}4.{Colors.ENDC} Generate Sample Files")
            print(f"{Colors.BLUE}5.{Colors.ENDC} View Protocol Information")
            print(f"{Colors.BLUE}6.{Colors.ENDC} Exit")
            
            try:
                choice = input(f"\n{Colors.YELLOW}Select option (1-6): {Colors.ENDC}").strip()
                
                if choice == '1':
                    self.subghz_wizard()
                elif choice == '2':
                    self.ir_wizard()
                elif choice == '3':
                    self.analysis_tools()
                elif choice == '4':
                    self.generate_samples()
                elif choice == '5':
                    self.view_protocols()
                elif choice == '6':
                    print(f"\n{Colors.GREEN}Thanks for using Flipper Generator! 🐬{Colors.ENDC}")
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please select 1-6.{Colors.ENDC}")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}Goodbye! 🐬{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.ENDC}")

    def subghz_wizard(self):
        """Interactive Sub-GHz file creation wizard"""
        print(f"\n{Colors.HEADER}🔵 Sub-GHz Protocol Wizard{Colors.ENDC}")
        
        # Protocol selection
        protocol = self.select_protocol("subghz")
        if not protocol:
            return
        
        # Frequency selection
        frequency = self.select_frequency()
        if not frequency:
            return
        
        if protocol == "RAW":
            raw_data = self.create_raw_subghz_data()
            if not raw_data:
                return
            
            output_file = self.get_output_filename("sub")
            self.create_subghz_file(
                protocol="RAW",
                frequency=frequency,
                raw_data=raw_data,
                output_file=output_file
            )
        else:
            # Get protocol-specific data
            key, data, te = self.get_protocol_data(protocol)
            repeat = self.get_repeat_count()
            
            output_file = self.get_output_filename("sub")
            
            # Build parameters for protocol
            params = {
                'protocol': protocol,
                'frequency': frequency,
                'key': key,
                'repeat': repeat,
                'output_file': output_file,
                'bit_count': self.subghz_protocols[protocol]['bits']
            }
            
            # Only add TE if the protocol needs it
            protocol_info = self.subghz_protocols[protocol]
            if protocol_info.get('needs_te', False) and te:
                params['te'] = te
            
            # Add data if provided
            if data:
                params['data'] = data
            
            self.create_subghz_file(**params)

    def ir_wizard(self):
        """Interactive IR file creation wizard"""
        print(f"\n{Colors.HEADER}🔴 Infrared Protocol Wizard{Colors.ENDC}")
        
        # Protocol selection
        protocol = self.select_protocol("ir")
        if not protocol:
            return
        
        if protocol == "RAW":
            raw_data = self.create_raw_ir_data()
            if not raw_data:
                return
            
            frequency = self.get_ir_frequency()
            duty_cycle = self.get_duty_cycle()
            
            output_file = self.get_output_filename("ir")
            self.create_ir_file(
                protocol="RAW",
                raw_data=raw_data,
                frequency=frequency,
                duty_cycle=duty_cycle,
                output_file=output_file
            )
        else:
            # Get address and command
            address, command = self.get_ir_codes(protocol)
            if not address or not command:
                return
            
            output_file = self.get_output_filename("ir")
            self.create_ir_file(
                protocol=protocol,
                address=address,
                command=command,
                output_file=output_file
            )

    def select_protocol(self, protocol_type: str) -> Optional[str]:
        """Interactive protocol selection"""
        protocols = self.subghz_protocols if protocol_type == "subghz" else self.ir_protocols
        
        print(f"\n{Colors.CYAN}Available {protocol_type.upper()} Protocols:{Colors.ENDC}")
        protocol_list = list(protocols.keys())
        
        for i, (name, info) in enumerate(protocols.items(), 1):
            print(f"{Colors.BLUE}{i:2d}.{Colors.ENDC} {name:15} - {info['description']}")
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Select protocol (1-{len(protocols)}) or 'q' to quit: {Colors.ENDC}").strip()
                if choice.lower() == 'q':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(protocol_list):
                    selected = protocol_list[idx]
                    print(f"{Colors.GREEN}Selected: {selected}{Colors.ENDC}")
                    return selected
                else:
                    print(f"{Colors.RED}Invalid choice. Enter 1-{len(protocols)} or 'q' to quit.{Colors.ENDC}")
            except (ValueError, KeyboardInterrupt):
                return None

    def select_frequency(self) -> Optional[int]:
        """Interactive frequency selection"""
        print(f"\n{Colors.CYAN}Frequency Selection:{Colors.ENDC}")
        
        freq_list = list(self.common_frequencies.items())
        for i, (name, freq) in enumerate(freq_list, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {name} ({freq:,} Hz)")
        print(f"{Colors.BLUE}{len(freq_list)+1}.{Colors.ENDC} Custom frequency")
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Select frequency: {Colors.ENDC}").strip()
                if choice.lower() == 'q':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(freq_list):
                    freq = freq_list[idx][1]
                    print(f"{Colors.GREEN}Selected: {freq:,} Hz{Colors.ENDC}")
                    return freq
                elif idx == len(freq_list):
                    return self.get_custom_frequency()
                else:
                    print(f"{Colors.RED}Invalid choice.{Colors.ENDC}")
            except (ValueError, KeyboardInterrupt):
                return None

    def get_custom_frequency(self) -> Optional[int]:
        """Get custom frequency input"""
        print(f"\n{Colors.CYAN}Flipper Zero frequency ranges:{Colors.ENDC}")
        print("• 300-348 MHz")
        print("• 387-464 MHz") 
        print("• 779-928 MHz")
        
        while True:
            try:
                freq_str = input(f"\n{Colors.YELLOW}Enter frequency in Hz: {Colors.ENDC}").strip()
                if freq_str.lower() == 'q':
                    return None
                
                # Handle common formats
                freq_str = freq_str.replace(',', '').replace(' ', '')
                if freq_str.lower().endswith('mhz'):
                    frequency = int(float(freq_str[:-3]) * 1000000)
                elif freq_str.lower().endswith('khz'):
                    frequency = int(float(freq_str[:-3]) * 1000)
                else:
                    frequency = int(freq_str)
                
                # Validate range
                valid_ranges = [(300000000, 348000000), (387000000, 464000000), (779000000, 928000000)]
                in_range = any(start <= frequency <= end for start, end in valid_ranges)
                
                if not in_range:
                    print(f"{Colors.YELLOW}Warning: {frequency:,} Hz may not work with Flipper Zero{Colors.ENDC}")
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return frequency
                
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}Invalid frequency format.{Colors.ENDC}")

    def create_raw_subghz_data(self) -> Optional[List[int]]:
        """Interactive RAW Sub-GHz data creation"""
        print(f"\n{Colors.CYAN}RAW Sub-GHz Data Creation{Colors.ENDC}")
        print("Options:")
        print(f"{Colors.BLUE}1.{Colors.ENDC} Manual entry (space-separated timing values)")
        print(f"{Colors.BLUE}2.{Colors.ENDC} Pattern generator")
        print(f"{Colors.BLUE}3.{Colors.ENDC} Load from file")
        
        choice = input(f"\n{Colors.YELLOW}Select method: {Colors.ENDC}").strip()
        
        if choice == '1':
            return self.manual_raw_entry()
        elif choice == '2':
            return self.pattern_generator_subghz()
        elif choice == '3':
            return self.load_raw_from_file()
        else:
            print(f"{Colors.RED}Invalid choice.{Colors.ENDC}")
            return None

    def create_raw_ir_data(self) -> Optional[List[int]]:
        """Interactive RAW IR data creation"""
        print(f"\n{Colors.CYAN}RAW IR Data Creation{Colors.ENDC}")
        print("Options:")
        print(f"{Colors.BLUE}1.{Colors.ENDC} Manual entry")
        print(f"{Colors.BLUE}2.{Colors.ENDC} Pattern generator")
        print(f"{Colors.BLUE}3.{Colors.ENDC} Load from file")
        print(f"{Colors.BLUE}4.{Colors.ENDC} Common IR patterns")
        
        choice = input(f"\n{Colors.YELLOW}Select method: {Colors.ENDC}").strip()
        
        if choice == '1':
            return self.manual_raw_entry()
        elif choice == '2':
            return self.pattern_generator_ir()
        elif choice == '3':
            return self.load_raw_from_file()
        elif choice == '4':
            return self.common_ir_patterns()
        else:
            print(f"{Colors.RED}Invalid choice.{Colors.ENDC}")
            return None

    def manual_raw_entry(self) -> Optional[List[int]]:
        """Manual raw data entry with helpers"""
        print(f"\n{Colors.CYAN}Manual RAW Data Entry{Colors.ENDC}")
        print("Enter timing values in microseconds, separated by spaces.")
        print("Positive values = ON time, Negative values = OFF time")
        print("Example: 9000 -4500 560 -560 560 -1690")
        print("Type 'help' for more info, 'q' to quit")
        
        while True:
            try:
                data_str = input(f"\n{Colors.YELLOW}Enter timing data: {Colors.ENDC}").strip()
                
                if data_str.lower() == 'q':
                    return None
                elif data_str.lower() == 'help':
                    self.show_raw_help()
                    continue
                
                # Parse the data
                raw_data = []
                for value in data_str.split():
                    raw_data.append(int(value))
                
                if len(raw_data) < 4:
                    print(f"{Colors.RED}Need at least 4 timing values{Colors.ENDC}")
                    continue
                
                print(f"{Colors.GREEN}Parsed {len(raw_data)} timing values{Colors.ENDC}")
                self.preview_timing(raw_data[:20])  # Show first 20 values
                
                confirm = input(f"{Colors.YELLOW}Use this data? (y/n): {Colors.ENDC}").strip().lower()
                if confirm == 'y':
                    return raw_data
                    
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}Invalid format. Use space-separated integers.{Colors.ENDC}")

    def pattern_generator_subghz(self) -> Optional[List[int]]:
        """Generate Sub-GHz patterns interactively"""
        print(f"\n{Colors.CYAN}Sub-GHz Pattern Generator{Colors.ENDC}")
        
        patterns = {
            "Simple On-Off": self.generate_simple_onoff,
            "Manchester": self.generate_manchester,
            "PWM": self.generate_pwm,
            "Custom Repeat": self.generate_custom_repeat
        }
        
        print("Available patterns:")
        pattern_list = list(patterns.keys())
        for i, name in enumerate(pattern_list, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {name}")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}Select pattern: {Colors.ENDC}")) - 1
            if 0 <= choice < len(pattern_list):
                pattern_name = pattern_list[choice]
                return patterns[pattern_name]()
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid choice{Colors.ENDC}")
        
        return None

    def generate_simple_onoff(self) -> List[int]:
        """Generate simple on-off pattern"""
        try:
            on_time = int(input("ON time (microseconds): "))
            off_time = int(input("OFF time (microseconds): "))
            repeats = int(input("Number of repeats: "))
            
            pattern = []
            for _ in range(repeats):
                pattern.extend([on_time, -off_time])
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.ENDC}")
            return []

    def generate_manchester(self) -> List[int]:
        """Generate Manchester encoded pattern"""
        try:
            bit_time = int(input("Bit time (microseconds): "))
            data = input("Binary data (e.g., 1010110): ").strip()
            
            pattern = []
            for bit in data:
                if bit == '1':
                    pattern.extend([bit_time//2, -bit_time//2])
                elif bit == '0':
                    pattern.extend([-bit_time//2, bit_time//2])
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.ENDC}")
            return []

    def generate_pwm(self) -> List[int]:
        """Generate PWM pattern"""
        try:
            short_pulse = int(input("Short pulse (microseconds): "))
            long_pulse = int(input("Long pulse (microseconds): "))
            gap = int(input("Gap between pulses (microseconds): "))
            data = input("Binary data (1=long, 0=short): ").strip()
            
            pattern = []
            for bit in data:
                if bit == '1':
                    pattern.extend([long_pulse, -gap])
                elif bit == '0':
                    pattern.extend([short_pulse, -gap])
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.ENDC}")
            return []

    def generate_custom_repeat(self) -> List[int]:
        """Generate custom repeating pattern"""
        try:
            print("Enter base pattern (space-separated values):")
            base_str = input().strip()
            base_pattern = [int(x) for x in base_str.split()]
            
            repeats = int(input("Number of repeats: "))
            gap = int(input("Gap between repeats (microseconds, 0 for none): "))
            
            pattern = []
            for i in range(repeats):
                pattern.extend(base_pattern)
                if gap > 0 and i < repeats - 1:
                    pattern.append(-gap)
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.ENDC}")
            return []

    def pattern_generator_ir(self) -> Optional[List[int]]:
        """Generate IR-specific patterns"""
        print(f"\n{Colors.CYAN}IR Pattern Generator{Colors.ENDC}")
        print("1. NEC-like pattern")
        print("2. RC5-like pattern")
        print("3. Custom IR pattern")
        
        choice = input("Select pattern: ").strip()
        
        if choice == '1':
            return self.generate_nec_like()
        elif choice == '2':
            return self.generate_rc5_like()
        elif choice == '3':
            return self.generate_simple_onoff()
        
        return None

    def generate_nec_like(self) -> List[int]:
        """Generate NEC-like IR pattern"""
        try:
            # NEC protocol basics
            pattern = [9000, -4500]  # Leader
            
            # Get data
            data = input("Enter 32-bit hex data (e.g., 0x12345678): ").strip()
            if data.startswith('0x'):
                data = data[2:]
            
            # Convert to binary
            binary = bin(int(data, 16))[2:].zfill(32)
            
            # Add bits (NEC uses 560µs pulses)
            for bit in binary:
                if bit == '1':
                    pattern.extend([560, -1690])  # Logical 1
                else:
                    pattern.extend([560, -560])   # Logical 0
            
            pattern.append(560)  # Stop bit
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid hex data{Colors.ENDC}")
            return []

    def generate_rc5_like(self) -> List[int]:
        """Generate RC5-like IR pattern"""
        try:
            bit_time = 889  # RC5 bit time
            data = input("Enter 13-bit binary data: ").strip()
            
            pattern = []
            for bit in data:
                if bit == '1':
                    pattern.extend([-bit_time, bit_time])
                elif bit == '0':
                    pattern.extend([bit_time, -bit_time])
            
            return pattern
        except ValueError:
            print(f"{Colors.RED}Invalid binary data{Colors.ENDC}")
            return []

    def common_ir_patterns(self) -> Optional[List[int]]:
        """Common IR patterns library"""
        print(f"\n{Colors.CYAN}Common IR Patterns{Colors.ENDC}")
        
        patterns = {
            "Power On/Off": [9000, -4500, 560, -1690, 560, -560, 560, -1690, 560],
            "Volume Up": [9000, -4500, 560, -560, 560, -1690, 560, -560, 560],
            "Volume Down": [9000, -4500, 560, -1690, 560, -1690, 560, -560, 560],
            "Channel Up": [9000, -4500, 560, -560, 560, -560, 560, -1690, 560],
            "Channel Down": [9000, -4500, 560, -1690, 560, -560, 560, -1690, 560]
        }
        
        pattern_list = list(patterns.keys())
        for i, name in enumerate(pattern_list, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {name}")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}Select pattern: {Colors.ENDC}")) - 1
            if 0 <= choice < len(pattern_list):
                pattern_name = pattern_list[choice]
                return patterns[pattern_name]
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid choice{Colors.ENDC}")
        
        return None

    def load_raw_from_file(self) -> Optional[List[int]]:
        """Load raw data from file"""
        filename = input(f"{Colors.YELLOW}Enter filename: {Colors.ENDC}").strip()
        
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
            
            # Try to parse as space-separated integers
            raw_data = [int(x) for x in content.split()]
            
            print(f"{Colors.GREEN}Loaded {len(raw_data)} values from {filename}{Colors.ENDC}")
            return raw_data
            
        except FileNotFoundError:
            print(f"{Colors.RED}File not found: {filename}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Invalid data format in file{Colors.ENDC}")
        
        return None

    def analysis_tools(self):
        """Signal analysis and conversion tools"""
        print(f"\n{Colors.HEADER}🔧 Signal Analysis Tools{Colors.ENDC}")
        print(f"{Colors.BLUE}1.{Colors.ENDC} Convert binary to timing")
        print(f"{Colors.BLUE}2.{Colors.ENDC} Analyze timing pattern")
        print(f"{Colors.BLUE}3.{Colors.ENDC} Calculate protocol parameters")
        print(f"{Colors.BLUE}4.{Colors.ENDC} Hex to binary converter")
        
        choice = input(f"\n{Colors.YELLOW}Select tool: {Colors.ENDC}").strip()
        
        if choice == '1':
            self.binary_to_timing()
        elif choice == '2':
            self.analyze_timing()
        elif choice == '3':
            self.calculate_parameters()
        elif choice == '4':
            self.hex_to_binary()

    def binary_to_timing(self):
        """Convert binary data to timing values"""
        print(f"\n{Colors.CYAN}Binary to Timing Converter{Colors.ENDC}")
        
        binary = input("Enter binary data: ").strip()
        short_pulse = int(input("Short pulse time (µs): "))
        long_pulse = int(input("Long pulse time (µs): "))
        
        encoding = input("Encoding type (pwm/manchester) [pwm]: ").strip().lower() or "pwm"
        
        timing = []
        if encoding == "pwm":
            for bit in binary:
                if bit == '1':
                    timing.extend([long_pulse, -short_pulse])
                elif bit == '0':
                    timing.extend([short_pulse, -short_pulse])
        elif encoding == "manchester":
            for bit in binary:
                if bit == '1':
                    timing.extend([short_pulse, -short_pulse])
                elif bit == '0':
                    timing.extend([-short_pulse, short_pulse])
        
        print(f"\n{Colors.GREEN}Generated timing:{Colors.ENDC}")
        print(" ".join(map(str, timing)))
        
        if input(f"\n{Colors.YELLOW}Save to file? (y/n): {Colors.ENDC}").lower() == 'y':
            filename = input("Filename: ").strip() or f"timing_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                f.write(" ".join(map(str, timing)))
            print(f"{Colors.GREEN}Saved to {filename}{Colors.ENDC}")

    def analyze_timing(self):
        """Analyze timing patterns"""
        print(f"\n{Colors.CYAN}Timing Pattern Analyzer{Colors.ENDC}")
        
        timing_str = input("Enter timing data (space-separated): ").strip()
        try:
            timing = [int(x) for x in timing_str.split()]
            
            print(f"\n{Colors.GREEN}Analysis Results:{Colors.ENDC}")
            print(f"Total values: {len(timing)}")
            print(f"Positive values: {len([x for x in timing if x > 0])}")
            print(f"Negative values: {len([x for x in timing if x < 0])}")
            
            positive_vals = [x for x in timing if x > 0]
            negative_vals = [abs(x) for x in timing if x < 0]
            
            if positive_vals:
                print(f"ON times - Min: {min(positive_vals)}µs, Max: {max(positive_vals)}µs, Avg: {sum(positive_vals)//len(positive_vals)}µs")
            
            if negative_vals:
                print(f"OFF times - Min: {min(negative_vals)}µs, Max: {max(negative_vals)}µs, Avg: {sum(negative_vals)//len(negative_vals)}µs")
                
        except ValueError:
            print(f"{Colors.RED}Invalid timing data{Colors.ENDC}")

    def calculate_parameters(self):
        """Calculate protocol parameters"""
        print(f"\n{Colors.CYAN}Protocol Parameter Calculator{Colors.ENDC}")
        
        print("1. Calculate timing element (TE) from bit rate")
        print("2. Calculate frequency from wavelength")
        print("3. Calculate bit count from key length")
        
        choice = input("Select calculation: ").strip()
        
        if choice == '1':
            try:
                bit_rate = float(input("Bit rate (bps): "))
                te = int(1000000 / bit_rate)  # Convert to microseconds
                print(f"Timing element: {te} µs")
            except ValueError:
                print(f"{Colors.RED}Invalid input{Colors.ENDC}")
        
        elif choice == '2':
            try:
                wavelength = float(input("Wavelength (cm): "))
                frequency = int(30000000000 / wavelength)  # Speed of light / wavelength
                print(f"Frequency: {frequency:,} Hz ({frequency/1000000:.2f} MHz)")
            except ValueError:
                print(f"{Colors.RED}Invalid input{Colors.ENDC}")
        
        elif choice == '3':
            try:
                key = input("Enter hex key: ").strip()
                key = key.replace('0x', '')
                bits = len(key) * 4
                print(f"Bit count: {bits} bits")
            except ValueError:
                print(f"{Colors.RED}Invalid hex key{Colors.ENDC}")

    def hex_to_binary(self):
        """Convert hex to binary"""
        print(f"\n{Colors.CYAN}Hex to Binary Converter{Colors.ENDC}")
        
        hex_data = input("Enter hex data: ").strip()
        try:
            hex_data = hex_data.replace('0x', '')
            binary = bin(int(hex_data, 16))[2:]
            print(f"Binary: {binary}")
            print(f"Length: {len(binary)} bits")
        except ValueError:
            print(f"{Colors.RED}Invalid hex data{Colors.ENDC}")

    def get_protocol_data(self, protocol: str) -> Tuple[str, str, int]:
        """Get protocol-specific data interactively - FIXED to use actual key byte lengths"""
        print(f"\n{Colors.CYAN}Protocol Data for {protocol}{Colors.ENDC}")
        
        protocol_info = self.subghz_protocols[protocol]
        
        # Use actual key byte length from protocol specification
        key_bytes = protocol_info['key_bytes']
        hex_chars = key_bytes * 2  # 2 hex chars per byte
        print(f"Key length: {key_bytes} bytes ({hex_chars} hex characters)")
        print(f"Protocol bits: {protocol_info['bits']} bits")
        
        key = input(f"{Colors.YELLOW}Enter hex key (or 'random' for random): {Colors.ENDC}").strip()
        
        if key.lower() == 'random':
            # Generate random hex string with correct byte length
            random_hex = ''.join(random.choice('0123456789ABCDEF') for _ in range(hex_chars))
            # Format with spaces between byte pairs
            key = ' '.join(random_hex[i:i+2] for i in range(0, len(random_hex), 2))
            print(f"Generated random key: {key}")
        else:
            # Validate and format key length
            if key:
                key = key.replace('0x', '').replace(' ', '').upper()
                if len(key) > hex_chars:
                    key = key[:hex_chars]  # Truncate if too long
                    print(f"{Colors.YELLOW}Key truncated to {hex_chars} characters{Colors.ENDC}")
                elif len(key) < hex_chars:
                    key = key.zfill(hex_chars)  # Pad with zeros if too short
                    print(f"{Colors.YELLOW}Key padded to {hex_chars} characters{Colors.ENDC}")
                
                # Format with spaces between byte pairs
                key = ' '.join(key[i:i+2] for i in range(0, len(key), 2))
        
        # Data (optional for most protocols)
        data = input(f"{Colors.YELLOW}Enter hex data (optional, press Enter to skip): {Colors.ENDC}").strip()
        if data:
            data = data.replace('0x', '').replace(' ', '').upper()
            # Format data with spaces between byte pairs too
            data = ' '.join(data[i:i+2] for i in range(0, len(data), 2))
        
        # TE only for protocols that need it
        te = None
        if protocol_info.get('needs_te', False):
            default_te = protocol_info.get('default_te', 400)
            te_input = input(f"{Colors.YELLOW}Timing element [{default_te}]: {Colors.ENDC}").strip()
            te = int(te_input) if te_input else default_te
        
        return key, data, te

    def get_ir_codes(self, protocol: str) -> Tuple[str, str]:
        """Get IR address and command codes"""
        print(f"\n{Colors.CYAN}IR Codes for {protocol}{Colors.ENDC}")
        
        protocol_info = self.ir_protocols[protocol]
        
        print(f"Address: {protocol_info['address_bits']} bits")
        print(f"Command: {protocol_info['command_bits']} bits")
        
        address = input(f"{Colors.YELLOW}Enter address (hex): {Colors.ENDC}").strip()
        command = input(f"{Colors.YELLOW}Enter command (hex): {Colors.ENDC}").strip()
        
        return address.upper(), command.upper()

    def get_output_filename(self, extension: str) -> str:
        """Get output filename from user"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"flipper_{timestamp}.{extension}"
        
        filename = input(f"{Colors.YELLOW}Output filename [{default_name}]: {Colors.ENDC}").strip()
        return filename if filename else default_name

    def get_repeat_count(self) -> int:
        """Get repeat count from user"""
        repeat_str = input(f"{Colors.YELLOW}Repeat count [1]: {Colors.ENDC}").strip()
        return int(repeat_str) if repeat_str else 1

    def get_ir_frequency(self) -> int:
        """Get IR carrier frequency"""
        freq_str = input(f"{Colors.YELLOW}IR frequency [35715 Hz]: {Colors.ENDC}").strip()
        return int(freq_str) if freq_str else 35715

    def get_duty_cycle(self) -> float:
        """Get PWM duty cycle"""
        duty_str = input(f"{Colors.YELLOW}Duty cycle [0.33]: {Colors.ENDC}").strip()
        return float(duty_str) if duty_str else 0.33

    def show_raw_help(self):
        """Show help for RAW data entry"""
        print(f"\n{Colors.CYAN}RAW Data Format Help:{Colors.ENDC}")
        print("• Positive numbers = signal ON time (microseconds)")
        print("• Negative numbers = signal OFF time (microseconds)")
        print("• Values typically range from 100 to 10000 µs")
        print("\nExamples:")
        print("• NEC IR: 9000 -4500 560 -560 560 -1690 560 -560")
        print("• Simple 433MHz: 500 -500 1000 -500 500 -1000")

    def preview_timing(self, data: List[int]):
        """Show a visual preview of timing data"""
        print(f"\n{Colors.CYAN}Timing Preview (first {len(data)} values):{Colors.ENDC}")
        for i, value in enumerate(data):
            state = "ON " if value > 0 else "OFF"
            print(f"{i:2d}: {state} {abs(value):4d}µs")

    def create_subghz_file(self, **kwargs) -> str:
        """Create Sub-GHz file with given parameters - MATCHES FLIPPER FORMAT"""
        lines = ["Filetype: Flipper SubGhz Key File", "Version: 1"]
        
        lines.append(f"Frequency: {kwargs['frequency']}")
        lines.append(f"Preset: {kwargs.get('preset', 'FuriHalSubGhzPresetOok270Async')}")
        lines.append(f"Protocol: {kwargs['protocol']}")
        
        if kwargs['protocol'] == 'RAW':
            lines.append(f"RAW_Data: {' '.join(map(str, kwargs['raw_data']))}")
        else:
            # Bit count (required for most protocols)
            if kwargs.get('bit_count'):
                lines.append(f"Bit: {kwargs['bit_count']}")
            
            # Key - already formatted with spaces in get_protocol_data
            if kwargs.get('key'):
                lines.append(f"Key: {kwargs['key']}")
            
            # Only add TE if specified (not all protocols need it)
            if kwargs.get('te'):
                lines.append(f"TE: {kwargs['te']}")
            
            # Data field (optional, also already formatted with spaces)
            if kwargs.get('data'):
                lines.append(f"Data: {kwargs['data']}")
            
            # Repeat count
            repeat = kwargs.get('repeat', 1)
            if repeat > 1:
                lines.append(f"Repeat: {repeat}")
        
        content = '\n'.join(lines) + '\n'
        filename = kwargs['output_file']
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"\n{Colors.GREEN}✅ Created: {os.path.abspath(filename)}{Colors.ENDC}")
        print(f"{Colors.CYAN}File contents:{Colors.ENDC}")
        print(content)
        return filename

    def create_ir_file(self, **kwargs) -> str:
        """Create IR file with given parameters"""
        lines = ["Filetype: IR signals file", "Version: 1"]
        
        if kwargs['protocol'] == 'RAW':
            lines.extend([
                "name: Custom_RAW",
                "type: raw",
                f"frequency: {kwargs.get('frequency', 38000)}",
                f"duty_cycle: {kwargs.get('duty_cycle', 0.33)}",
                f"data: {' '.join(map(str, kwargs['raw_data']))}"
            ])
        else:
            lines.extend([
                f"name: Custom_{kwargs['protocol']}",
                "type: parsed",
                f"protocol: {kwargs['protocol']}",
                f"address: {kwargs['address']}",
                f"command: {kwargs['command']}"
            ])
        
        content = '\n'.join(lines) + '\n'
        filename = kwargs['output_file']
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"\n{Colors.GREEN}✅ Created: {os.path.abspath(filename)}{Colors.ENDC}")
        print(f"{Colors.CYAN}File contents:{Colors.ENDC}")
        print(content)
        return filename

    def generate_samples(self):
        """Generate sample files"""
        print(f"\n{Colors.HEADER}📋 Sample File Generator{Colors.ENDC}")
        
        # Create sample Sub-GHz files
        print("Creating sample Sub-GHz files...")
        
        # Princeton sample (with TE since it needs it) - CORRECTED to 8-byte key
        self.create_subghz_file(
            protocol="Princeton",
            frequency=433920000,
            key="00 00 00 00 00 95 D5 D4",  # 8 bytes as per GitHub example
            bit_count=24,
            te=400,
            output_file="sample_princeton.sub"
        )
        
        # Holtek sample (no TE needed) - CORRECTED to 10-byte key  
        self.create_subghz_file(
            protocol="Holtek",
            frequency=418000000,
            key="00 00 52 AA AA BB CC DD EE FF",  # 10 bytes for 40-bit protocol
            bit_count=40,
            output_file="sample_holtek.sub"
        )
        
        # RAW sample
        sample_raw_data = [500, -500, 1000, -500, 500, -1000, 1000, -500]
        self.create_subghz_file(
            protocol="RAW",
            frequency=315000000,
            raw_data=sample_raw_data,
            output_file="sample_raw.sub"
        )
        
        # Create sample IR files
        print("\nCreating sample IR files...")
        
        # NEC sample
        self.create_ir_file(
            protocol="NEC",
            address="04",
            command="08",
            output_file="sample_nec.ir"
        )
        
        # IR RAW sample
        sample_ir_raw = [9000, -4500, 560, -560, 560, -1690, 560, -560, 560]
        self.create_ir_file(
            protocol="RAW",
            raw_data=sample_ir_raw,
            frequency=38000,
            duty_cycle=0.33,
            output_file="sample_ir_raw.ir"
        )
        
        print(f"\n{Colors.GREEN}Sample files created successfully!{Colors.ENDC}")

    def view_protocols(self):
        """Display protocol information"""
        print(f"\n{Colors.HEADER}📖 Protocol Information{Colors.ENDC}")
        
        print(f"\n{Colors.CYAN}Sub-GHz Protocols:{Colors.ENDC}")
        for name, info in self.subghz_protocols.items():
            if name != "RAW":
                te_info = f", TE required" if info.get('needs_te') else ", no TE"
                print(f"• {name:15} - {info['bits']:2d} bits, {info['key_bytes']:2d} key bytes{te_info} - {info['description']}")
            else:
                print(f"• {name:15} - Custom timing data - {info['description']}")
        
        print(f"\n{Colors.CYAN}IR Protocols:{Colors.ENDC}")
        for name, info in self.ir_protocols.items():
            if name != "RAW":
                addr_bits = info['address_bits']
                cmd_bits = info['command_bits']
                print(f"• {name:15} - Addr:{addr_bits:2d}b, Cmd:{cmd_bits:2d}b - {info['description']}")
            else:
                print(f"• {name:15} - Custom timing data - {info['description']}")
        
        print(f"\n{Colors.CYAN}Supported Frequencies:{Colors.ENDC}")
        for name, freq in self.common_frequencies.items():
            print(f"• {name} ({freq:,} Hz)")
        
        print(f"\n{Colors.CYAN}Flipper Zero Frequency Ranges:{Colors.ENDC}")
        print("• 300-348 MHz")
        print("• 387-464 MHz")
        print("• 779-928 MHz")

def main():
    """Main application entry point"""
    # Check if running in interactive mode or with command line args
    if len(sys.argv) > 1:
        # Command line mode (original functionality)
        parser = argparse.ArgumentParser(description="Flipper Zero Protocol Generator")
        parser.add_argument('--interactive', '-i', action='store_true', 
                          help='Start interactive mode')
        parser.add_argument('--no-color', action='store_true',
                          help='Disable colored output')
        
        args = parser.parse_args()
        
        if args.no_color:
            Colors.disable()
        
        if args.interactive:
            # Interactive mode
            generator = InteractiveFlipperGenerator()
            generator.print_banner()
            generator.main_menu()
        else:
            print("Command line mode not implemented in this version.")
            print("Use --interactive or -i for interactive mode.")
    else:
        # Default to interactive mode
        generator = InteractiveFlipperGenerator()
        generator.print_banner()
        generator.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}Thanks for using Flipper Generator! 🐬{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)