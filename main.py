import os
import subprocess
import argparse

from inference_serving.scheduler import *
from inference_serving.request import *
from inference_serving.utils import *
from inference_serving.control import *
from inference_serving.memory_model import *
from inference_serving.generate_graph import *
from inference_serving.generate_trace import *
from inference_serving.pim import *
from inference_serving.control import *
from inference_serving.config_generator import *
from inference_serving.request_api import RequestAPI
from inference_serving.http_server import LLMServingServer


def main():
    ################################################################################################
    # LLMServingSim runs in astra-sim directory for easy path configuration
    # your relative path should start from astra-sim directory
    cwd = os.getcwd()
    astra_sim = os.path.join(cwd, "astra-sim")
    os.chdir(astra_sim)
    parser = argparse.ArgumentParser(description='LLMServingSim') 

    parser.add_argument('--model_name', type=str, help='Name of the model', default='gpt3-6.7b')
    parser.add_argument('--hardware', type=str, help='type of a hardware (e.g. A100)', default='RTX3090')
    parser.add_argument('--npu_num', type=int, help='# of NPUs', default=16)
    parser.add_argument('--max_batch', type=int, help='maximum size of the batch', default=0)
    parser.add_argument('--npu_group', type=int, help='npu_group to control parallelism', default=1)
    parser.add_argument('--npu_mem', type=int, help='npu memory in GB', default=40)
    parser.add_argument('--local_bw', type=int, help='bandwidth of local (device) memory in GB', default=1024)
    parser.add_argument('--remote_bw', type=int, help='bandwidth of remote (host) memory in GB', default=512)
    parser.add_argument('--link_bw', type=int, help='bandwidth of link in GB', default=256)
    parser.add_argument('--link_latency', type=int, help='latency of link in ns', default=0)
    parser.add_argument('--fp', type=int, help='size of floating point in bit', default=16)
    parser.add_argument('--block_size', type=int, help='kv cache block size unit of tokens', default=8)
    parser.add_argument('--dataset', type=str, help='dataset path', default=None)
    parser.add_argument('--output', type=str, help='output path', default=None)
    parser.add_argument('--gen', action='store_false', default=True, help='skip initiation phase')
    parser.add_argument('--req_num', type=int, help='number of requests to use', default=100)
    parser.add_argument('--log_interval', type=float, help='interval to log throughput (sec)', default=0.5)
    parser.add_argument('--verbose', action='store_true', default=False, help='make verbose')
    parser.add_argument('--idle_mode', action='store_true', default=False, help='start service without generating requests')
    parser.add_argument('--http_port', type=int, help='HTTP server port for receiving requests', default=8000)
    parser.add_argument('--http_host', type=str, help='HTTP server host', default='localhost')

    args = parser.parse_args()

    model=args.model_name
    hardware=args.hardware
    npu_num=args.npu_num
    max_batch=args.max_batch if args.max_batch != 0 else float('inf')       # 0 means infinite batch size
    npu_group=args.npu_group                                                # configure this to control parallelism      *if npu_group == 1: tensor parallelism, npu_num == npu_group: pipeline parallelism
    npu_mem=args.npu_mem                                                    # npu local mem (hbm) in GB     *if pim pool mode, it is size of pim and kv cache is in pim
    block_size=args.block_size                                              # kv block size of vLLM  
    fp=args.fp
    dataset=args.dataset
    output_file=args.output
    is_init=args.gen
    local_bw=args.local_bw
    link_bw=args.link_bw
    link_latency = args.link_latency
    remote_bw=args.remote_bw
    req_num=args.req_num
    log_interval=args.log_interval
    verbose=args.verbose
    idle_mode=args.idle_mode
    http_port=args.http_port
    http_host=args.http_host

    # Automatic network, memory configuration
    # If you want to set more specific information such as latency, look at config_generator.py and each json file
    network=create_network_config(astra_sim, npu_num, npu_group, link_bw, link_latency)
    memory=set_remote_bandwidth(astra_sim+"/inputs/remote_memory/per_npu_memory_expansion.json", remote_bw)
    binary=astra_sim+"/build/astra_analytical/build/AnalyticalAstra/bin/AnalyticalAstra"
    system=astra_sim+"/inputs/system/system.json"
    ################################################################################################

    scheduler = Scheduler(model, max_batch, npu_num, npu_group, npu_mem, fp, block_size, req_num, verbose)
    controller = Controller(npu_num, verbose)
    
    # Create Request API for dynamic request management
    request_api = None
    http_server = None
    
    if idle_mode:
        request_api = RequestAPI(scheduler)
        # Start HTTP server for receiving external requests
        try:
            http_server = LLMServingServer(request_api, http_host, http_port)
            http_server.start()
        except Exception as e:
            print(f"Warning: Failed to start HTTP server: {e}")
            print("Continuing without HTTP server...")

    if not idle_mode:
        if dataset != None:
            # generate possion
            scheduler.generate(dataset, is_init=is_init)
        else:
            # Manually adding request
            for i in range(16):      # model, seq_len, end_len, arrival_time
                scheduler.addRequest([model, 128, 129, 0])
    else:
        print("Starting LLMServingSim in idle mode - no requests will be generated")
        print("Service is ready to accept requests...")
        # In idle mode, don't generate any requests initially

    # Simulator start
    current = 0 # current tick of the system
    sys = 0 # current system id (NPU id)
    id = 0 # id of the request

    # Calculating Simulator's Throughput
    throughput = []
    prompt_th = 0    # Avg Prompt Throguhput per Sec
    gen_th = 0       # Avg Generation Throughput per Sec
    last_log = 0    # last logged time
    FREQ = 1000000000 # 1 GHz
    INTERVAL = log_interval*FREQ
    RATIO = FREQ//INTERVAL
    total_prompt = 0
    total_gen = 0
    total_latency = 0
    requests = 0

    # set Event Handler that waits until first request arrive
    # Make Event trace
    if idle_mode:
        # In idle mode, create a minimal event handler
        generate_event(1)  # Create a minimal 1ns event
    else:
        generate_event(scheduler.get_first_arrival_time())
    # Make Chakra Grapth
    generate_graph(None, hardware, npu_num, event=True)
    # set first workload file
    workload = get_workload(None, hardware, event=True)
    # run subprocess
    args = [binary, "--workload-configuration="+workload, "--system-configuration="+system, "--network-configuration="+network, "--remote-memory-configuration="+memory]
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


    # Starting simulation, one while loop processes one iteration
    while True:
        out = controller.read_wait(p)
        out_dict = controller.parse_output(out[-2])

        if out_dict != None:
            sys = out_dict['sys']
            id = out_dict['id']
            current = out_dict['cycle']


        # check request is done
        prompt_t, gen_t, req_cnt = scheduler.add_done(id, sys, current)
        # add tokens in throughput
        prompt_th += prompt_t
        total_prompt += prompt_t
        gen_th += gen_t
        total_gen += gen_t
        requests += req_cnt

        # schedule requests
        new_req = scheduler.schedule(current, sys, id)
        # no runnable batch
        if new_req == None:
            controller.write_flush(p, "pass")
        else:
            if sys == 0:
                generate_trace(new_req, hardware, npu_num, npu_group, fp)
                generate_graph(new_req, hardware, npu_num)
            workload = get_workload(new_req, hardware)
            controller.write_flush(p, workload)

        # check time to store throughput
        if current > last_log + INTERVAL:
            # store the prompt
            throughput.append((prompt_th*RATIO, gen_th*RATIO))
            last_log += INTERVAL
            print(f"[{last_log/FREQ}s] Avg Throughput: propmt: {prompt_th*RATIO}, generation: {gen_th*RATIO}")
            prompt_th = 0
            gen_th = 0

        
        if scheduler.is_request_empty():
            if idle_mode:
                # In idle mode, keep the service running and wait for new requests
                print(f"[{current/FREQ:.3f}s] Service is idle, waiting for requests...")
                controller.write_flush(p, "pass")  # Tell ASTRA-Sim to continue waiting
                # You could add logic here to accept new requests dynamically
                # For now, we'll just keep the service running
                import time
                time.sleep(1)  # Wait 1 second before checking again
                continue
            else:
                throughput.append((prompt_th*RATIO, gen_th*RATIO))
                last_log += INTERVAL
                print(f"[{last_log/FREQ}s] Avg Throughput: propmt: {prompt_th*RATIO}, generation: {gen_th*RATIO}")
                print("---------------------------")
                print("Exiting The Simulator")
                if scheduler.memory.weight == scheduler.memory.used_mem:
                    print("Memory Is All Freed")
                else:
                    print("Unfreed Memory Exists")
                controller.write_flush(p, "exit")
                break

    # Cleanup HTTP server
    if http_server:
        try:
            http_server.stop()
        except Exception as e:
            print(f"Error stopping HTTP server: {e}")

    # check all requests are well done
    controller.check_end(p)

    # print throughput results
    scheduler.print_result()
    total_latency = current/FREQ
    print('---------------------------')
    print('Throughput Results')
    print('---------------------------')
    print(f"Total prompts: {total_prompt} tokens")
    print(f"Total generation: {total_gen} tokens")
    print(f"Throughput per {1/RATIO} sec: {throughput}")
    print(f"Total clocks: {current} ticks")
    print(f"Total latency: {total_latency:.3f} s")
    print(f"Average prompt throughput: {total_prompt/total_latency:.3f} token/s")
    print(f"Average generation throughput: {total_gen/total_latency:.3f} token/s")
    print(f"Requests per second: {requests/total_latency:.3f} request/s")
    print('---------------------------')

    if output_file != None:
        if verbose:
            print(f"Saving each request's information to output file: {output_file}")
        scheduler.save_output(output_file)
    

if __name__ == "__main__":
    main()
