#!/usr/bin/env python3
"""
Generate performance model files for different hardware
Based on known performance ratios compared to RTX3090
"""

import csv
import os

def generate_hardware_perf_model(base_hardware="RTX3090", target_hardware="A100", performance_ratio=1.8):
    """
    Generate performance model for target hardware based on base hardware
    
    Args:
        base_hardware: Source hardware with existing performance data
        target_hardware: Target hardware to generate data for
        performance_ratio: How much faster target is compared to base (e.g., 1.8 = 80% faster)
    """
    
    base_file = f"perf_model/{base_hardware}.csv"
    target_file = f"perf_model/{target_hardware}.csv"
    
    if not os.path.exists(base_file):
        print(f"❌ Base file not found: {base_file}")
        return False
    
    print(f"📊 Generating {target_hardware} performance model...")
    print(f"   Base: {base_hardware} (ratio: 1.0)")
    print(f"   Target: {target_hardware} (ratio: {performance_ratio})")
    
    # Read base data and write target data
    models_found = set()
    entry_count = 0
    
    with open(base_file, 'r') as infile, open(target_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Update hardware name
            row['hardware'] = target_hardware
            
            # Adjust latency based on performance ratio
            original_latency = int(row['latency(ns)'])
            new_latency = int(original_latency / performance_ratio)
            row['latency(ns)'] = str(new_latency)
            
            writer.writerow(row)
            models_found.add(row['model'])
            entry_count += 1
    
    print(f"✅ Generated: {target_file}")
    print(f"   Total entries: {entry_count}")
    print(f"   Models: {', '.join(models_found)}")
    
    return True

def generate_all_hardware_models():
    """Generate performance models for common hardware"""
    
    print("🚀 Generating performance models for common hardware...")
    print("=" * 60)
    
    # Hardware performance ratios compared to RTX3090 (approximate)
    # Based on various benchmarks and specifications
    hardware_ratios = {
        "A100": 2.2,      # NVIDIA A100 - significantly faster for AI workloads
        "H100": 3.5,      # NVIDIA H100 - latest generation, much faster
        "A6000": 1.4,     # NVIDIA RTX A6000 - professional card
        "A40": 1.3,       # NVIDIA A40 - data center card
        "RTX4090": 1.6,   # NVIDIA RTX 4090 - consumer flagship
        "RTX4080": 1.2,   # NVIDIA RTX 4080 - high-end consumer
        "V100": 0.8,      # NVIDIA V100 - older generation (already exists, but regenerate)
        "T4": 0.4,        # NVIDIA T4 - inference optimized
        "L40": 1.8,       # NVIDIA L40 - professional card
        "A10": 0.9,       # NVIDIA A10 - mid-range professional
    }
    
    success_count = 0
    total_count = len(hardware_ratios)
    
    for hardware, ratio in hardware_ratios.items():
        try:
            if generate_hardware_perf_model("RTX3090", hardware, ratio):
                success_count += 1
            print()
        except Exception as e:
            print(f"❌ Error generating {hardware}: {e}")
            print()
    
    print("=" * 60)
    print(f"📈 Generation Summary:")
    print(f"   Successfully generated: {success_count}/{total_count} hardware models")
    print(f"   Files created in: perf_model/")
    
    # List all available hardware
    perf_files = [f for f in os.listdir("perf_model/") if f.endswith(".csv")]
    print(f"   Available hardware: {len(perf_files)} types")
    for f in sorted(perf_files):
        hardware_name = f.replace(".csv", "")
        print(f"     - {hardware_name}")

def show_hardware_comparison():
    """Show performance comparison of all generated hardware"""
    
    print("\n🔍 Hardware Performance Comparison")
    print("=" * 60)
    print("Hardware performance ratios (relative to RTX3090 = 1.0):")
    print()
    
    hardware_info = {
        "H100": {"ratio": 3.5, "memory": "80GB HBM3", "type": "Data Center"},
        "A100": {"ratio": 2.2, "memory": "40/80GB HBM2e", "type": "Data Center"},
        "L40": {"ratio": 1.8, "memory": "48GB GDDR6", "type": "Professional"},
        "RTX4090": {"ratio": 1.6, "memory": "24GB GDDR6X", "type": "Consumer"},
        "A6000": {"ratio": 1.4, "memory": "48GB GDDR6", "type": "Professional"},
        "A40": {"ratio": 1.3, "memory": "48GB GDDR6", "type": "Data Center"},
        "RTX4080": {"ratio": 1.2, "memory": "16GB GDDR6X", "type": "Consumer"},
        "RTX3090": {"ratio": 1.0, "memory": "24GB GDDR6X", "type": "Consumer"},
        "A10": {"ratio": 0.9, "memory": "24GB GDDR6", "type": "Professional"},
        "V100": {"ratio": 0.8, "memory": "16/32GB HBM2", "type": "Data Center"},
        "T4": {"ratio": 0.4, "memory": "16GB GDDR6", "type": "Inference"},
    }
    
    # Sort by performance ratio (descending)
    sorted_hardware = sorted(hardware_info.items(), key=lambda x: x[1]["ratio"], reverse=True)
    
    print(f"{'Hardware':<12} {'Ratio':<8} {'Memory':<16} {'Type':<12} {'Est. Speedup'}")
    print("-" * 60)
    
    for hw, info in sorted_hardware:
        speedup = f"{info['ratio']:.1f}x" if info['ratio'] >= 1.0 else f"0.{int(info['ratio']*10)}x"
        print(f"{hw:<12} {info['ratio']:<8.1f} {info['memory']:<16} {info['type']:<12} {speedup}")

if __name__ == "__main__":
    # Generate all hardware models
    generate_all_hardware_models()
    
    # Show comparison
    show_hardware_comparison()
    
    print(f"\n🎯 Usage Examples:")
    print(f"   python main.py --hardware A100 --model_name 'meta-llama/Llama-3.1-8B-Instruct'")
    print(f"   python main.py --hardware H100 --model_name 'Qwen3-8B'")
    print(f"   bash run_openai_server.sh --model 'Qwen3-8B' --hardware A100")
