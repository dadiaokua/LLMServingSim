#!/usr/bin/env python3
"""
Extend performance model files to support more models
Add Qwen3-8B, OPT-6.7B and other models to all hardware performance files
"""

import csv
import os
import glob

def get_available_models():
    """Get all available model configurations"""
    models = []
    
    # Scan model_configs directory
    for root, dirs, files in os.walk("model_configs"):
        for file in files:
            if file.endswith(".json"):
                # Extract model name from path
                rel_path = os.path.relpath(os.path.join(root, file), "model_configs")
                model_name = rel_path.replace(".json", "")
                models.append(model_name)
    
    return models

def estimate_model_performance_ratio(base_model, target_model):
    """
    Estimate performance ratio between models based on their specifications
    This is a rough estimation based on model size and architecture
    """
    
    # Load model configs to compare
    try:
        import sys
        sys.path.append('.')
        from inference_serving.utils import get_config
        
        base_config = get_config(base_model)
        target_config = get_config(target_model)
        
        if not base_config or not target_config:
            return 1.0  # Default to same performance
        
        # Calculate rough complexity ratio based on:
        # - Number of layers
        # - Hidden size
        # - Vocabulary size
        
        base_complexity = (
            base_config.get('num_hidden_layers', 32) * 
            base_config.get('hidden_size', 4096) * 
            (base_config.get('vocab_size', 50000) / 50000)  # Normalize vocab impact
        )
        
        target_complexity = (
            target_config.get('num_hidden_layers', 32) * 
            target_config.get('hidden_size', 4096) * 
            (target_config.get('vocab_size', 50000) / 50000)
        )
        
        ratio = target_complexity / base_complexity
        
        print(f"   Model complexity ratio: {base_model} -> {target_model} = {ratio:.2f}")
        return ratio
        
    except Exception as e:
        print(f"   Warning: Could not calculate complexity ratio: {e}")
        return 1.0

def add_model_to_perf_file(perf_file, base_model, target_model):
    """Add target model data to performance file based on base model"""
    
    print(f"   Adding {target_model} to {perf_file}...")
    
    # Calculate performance ratio
    perf_ratio = estimate_model_performance_ratio(base_model, target_model)
    
    # Read existing data
    rows = []
    base_model_rows = []
    
    with open(perf_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            rows.append(row)
            if row['model'] == base_model:
                base_model_rows.append(row)
    
    if not base_model_rows:
        print(f"   Warning: No data found for base model {base_model}")
        return False
    
    # Check if target model already exists
    existing_models = set(row['model'] for row in rows)
    if target_model in existing_models:
        print(f"   {target_model} already exists in {perf_file}")
        return True
    
    # Generate new rows for target model
    new_rows = []
    for base_row in base_model_rows:
        new_row = base_row.copy()
        new_row['model'] = target_model
        
        # Adjust latency based on complexity ratio
        original_latency = int(base_row['latency(ns)'])
        new_latency = int(original_latency * perf_ratio)
        new_row['latency(ns)'] = str(new_latency)
        
        new_rows.append(new_row)
    
    # Write back all data
    all_rows = rows + new_rows
    
    with open(perf_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"   ✅ Added {len(new_rows)} entries for {target_model}")
    return True

def extend_all_perf_models():
    """Extend all performance model files to support more models"""
    
    print("🚀 Extending performance models to support more models...")
    print("=" * 60)
    
    # Get available models
    available_models = get_available_models()
    print(f"📋 Found {len(available_models)} model configurations:")
    for model in available_models:
        print(f"   - {model}")
    print()
    
    # Get all performance model files
    perf_files = glob.glob("perf_model/*.csv")
    print(f"🖥️ Found {len(perf_files)} hardware performance files:")
    for pf in sorted(perf_files):
        hardware = os.path.basename(pf).replace('.csv', '')
        print(f"   - {hardware}")
    print()
    
    # Base model (the one we have data for)
    base_model = "meta-llama/Llama-3.1-8B-Instruct"
    
    # Target models to add
    target_models = [model for model in available_models if model != base_model]
    
    if not target_models:
        print("ℹ️ No additional models to add.")
        return
    
    print(f"🎯 Adding {len(target_models)} models to {len(perf_files)} hardware files...")
    print()
    
    success_count = 0
    total_operations = len(perf_files) * len(target_models)
    
    for perf_file in sorted(perf_files):
        hardware = os.path.basename(perf_file).replace('.csv', '')
        print(f"🔧 Processing {hardware}...")
        
        for target_model in target_models:
            try:
                if add_model_to_perf_file(perf_file, base_model, target_model):
                    success_count += 1
            except Exception as e:
                print(f"   ❌ Error adding {target_model}: {e}")
        
        print()
    
    print("=" * 60)
    print(f"📊 Extension Summary:")
    print(f"   Successful operations: {success_count}/{total_operations}")
    print(f"   Models added to each hardware: {len(target_models)}")
    print(f"   Hardware types updated: {len(perf_files)}")

def show_model_support_matrix():
    """Show which models are supported on which hardware"""
    
    print("\n📋 Model Support Matrix")
    print("=" * 60)
    
    # Get all performance files
    perf_files = glob.glob("perf_model/*.csv")
    hardware_list = sorted([os.path.basename(pf).replace('.csv', '') for pf in perf_files])
    
    # Get models from first file (should be consistent across all files)
    if perf_files:
        with open(perf_files[0], 'r') as f:
            reader = csv.DictReader(f)
            models = sorted(set(row['model'] for row in reader))
        
        print(f"{'Model':<35} {'Hardware Support'}")
        print("-" * 60)
        
        for model in models:
            print(f"{model:<35} {len(hardware_list)} types")
        
        print(f"\nSupported Hardware: {', '.join(hardware_list)}")
        print(f"Total Combinations: {len(models)} models × {len(hardware_list)} hardware = {len(models) * len(hardware_list)} configs")

if __name__ == "__main__":
    # Extend all performance models
    extend_all_perf_models()
    
    # Show support matrix
    show_model_support_matrix()
    
    print(f"\n🎯 Usage Examples:")
    print(f"   # Use Qwen3-8B with A100")
    print(f"   python main.py --model_name 'qwen/Qwen3-8B' --hardware A100")
    print(f"   ")
    print(f"   # Use OPT-6.7B with H100")
    print(f"   python main.py --model_name 'facebook/opt-6.7b' --hardware H100")
    print(f"   ")
    print(f"   # Start OpenAI server with Qwen3-8B on V100")
    print(f"   bash run_openai_server.sh --model 'qwen/Qwen3-8B' --hardware V100")
