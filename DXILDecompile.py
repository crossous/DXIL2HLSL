import argparse
import sys
import os
import os.path
import re
import tempfile
import subprocess

def create_temporary(suff = ''):
    f, path = tempfile.mkstemp(suffix = suff)
    os.close(f)
    return path

def process_shader(args):
    # call_env = {**os.environ, 'PATH': f'{os.path.dirname(__file__)};' + os.environ['PATH']}
    os.chdir(os.path.dirname(__file__))
    dxil_spirv_cmd = ['dxil-spirv']
    spirv_cross_cmd = ['spirv-cross']

    if args.dxil_spirv_args != "":
        dxil_spirv_cmd += re.split(r'\s+', args.dxil_spirv_args)
    if args.spirv_cross_args != "":
        spirv_cross_cmd += re.split(r'\s+', args.spirv_cross_args)

    temp_spirv = False
    spirv_path = ""

    # dxil-spirv
    if "--output" not in dxil_spirv_cmd:
        spirv_path = create_temporary('spv')
        dxil_spirv_cmd.append("--output")
        dxil_spirv_cmd.append(spirv_path)
        temp_spirv = True
    else:
        spirv_path = dxil_spirv_cmd[dxil_spirv_cmd.index("--output") + 1]

    dxil_spirv_cmd.append(args.inputfile)
    # print("//call: " + ' '.join(dxil_spirv_cmd))
    subprocess.check_call(dxil_spirv_cmd)

    # spirv-cross
    temp_hlsl = False

    if not args.output:
        temp_hlsl = True
        args.output = create_temporary('hlsl')

    spirv_cross_cmd.append("--output")
    spirv_cross_cmd.append(args.output)

    if "--vulkan-semantics" not in spirv_cross_cmd:
        spirv_cross_cmd.append("--vulkan-semantics")

    if "--shader-model" not in spirv_cross_cmd:
        spirv_cross_cmd.append("--shader-model")
        spirv_cross_cmd.append("60")

    if "--hlsl" not in spirv_cross_cmd:
        spirv_cross_cmd.append("--hlsl")

    spirv_cross_cmd.append(spirv_path)
    # print("//call: " + ' '.join(spirv_cross_cmd))
    subprocess.check_call(spirv_cross_cmd)

    # with open(args.output) as f:
    #     print(''.join(f.readlines()))

    if temp_spirv:
        os.remove(spirv_path)

    if temp_hlsl:
        os.remove(args.output)

def main():
    parser = argparse.ArgumentParser(description = 'Script for decompile dxil to hlsl.')
    parser.add_argument('inputfile',
        help = 'dxil input file')
    parser.add_argument('--output',
        help = 'hlsl output file')
    parser.add_argument('--dxil-spirv-args',
        help = 'dxil-spirv.exe call args, need enclosed in double quotation marks, eg. --dxil-spirv-args="--glsl --asm --entry name"', default='')
    parser.add_argument('--spirv-cross-args',
        help = 'dxil-spirv.exe call args, need enclosed in double quotation mark, eg. --spirv-cross-args="--help --hlsl --reflect --entry name"', default='')
    args = parser.parse_args()
    if not args.inputfile:
        sys.stderr.write('Need shader folder.\n')
        sys.exit(1)

    process_shader(args)

if __name__ == '__main__':
    main()